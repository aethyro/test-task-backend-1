from datetime import datetime
from uuid import UUID

from app.models.pull_requests import PRStatus, PullRequest
from app.models.team_members import TeamMember
from app.models.pull_request_reviewers import PullRequestReviewer
from app.models.users import User
from app.services.pull_requests.errors import (
    PullRequestAlreadyExistsError,
    PullRequestMergedError,
    PullRequestNotFoundError,
    ReplacementCandidateNotFoundError,
    ReviewerNotAssignedError,
)
from app.services.pull_request_reviewers.pull_request_reviewers_service import (
    PullRequestReviewerService,
)
from app.services.pull_requests.schemas import (
    PullRequestCreate,
    PullRequestDto,
    PullRequestShort,
    PullRequestReassign,
)
from app.services.teams.errors import TeamNotFoundError
from app.services.users.errors import UserNotFoundError


class PullRequestService:
    @staticmethod
    async def create_pull_request(payload: PullRequestCreate) -> PullRequest:
        author_id = payload.author_id

        exists = await User.filter(id=author_id).exists()
        if not exists:
            raise UserNotFoundError(f"Пользователь с id {author_id} не найден", status_code=404)

        if await PullRequest.filter(id=payload.pull_request_id).exists():
            raise PullRequestAlreadyExistsError(
                f"Pull request с id {payload.pull_request_id} уже существует"
            )

        author_team = await TeamMember.filter(user_id=author_id).first()
        if not author_team:
            raise TeamNotFoundError("Команда автора не найдена", status_code=404, code="NOT_FOUND")

        pr = await PullRequest.create(
            id=payload.pull_request_id,
            title=payload.pull_request_name,
            author_id=author_id,
            status=PRStatus.OPEN,
        )

        await PullRequestReviewerService.add_pull_request_reviewers(
            pr.id, author_team.team_id, author_id
        )

        return pr

    @staticmethod
    async def merge_pull_request(pr_id: UUID) -> PullRequest:
        pr = await PullRequest.filter(id=pr_id).first()
        if not pr:
            raise PullRequestNotFoundError(f"Pull request с id {pr_id} не найден")

        if pr.status != PRStatus.MERGED:
            pr.status = PRStatus.MERGED
            pr.merged_at = pr.merged_at or datetime.utcnow()
            await pr.save()

        return pr

    @staticmethod
    async def reassign_pull_request(
        pr_id: UUID, payload: PullRequestReassign
    ) -> tuple[PullRequest, UUID]:
        pr = await PullRequest.filter(id=pr_id).first()
        if not pr:
            raise PullRequestNotFoundError(f"Pull request с id {pr_id} не найден")

        if pr.status == PRStatus.MERGED:
            raise PullRequestMergedError("Нельзя переназначить ревьюера у MERGED PR")

        old_reviewer = await User.filter(id=payload.old_user_id).first()
        if not old_reviewer:
            raise UserNotFoundError(f"Пользователь с id {payload.old_user_id} не найден")

        assigned = await PullRequestReviewer.filter(
            pr_id=pr_id, reviewer_id=payload.old_user_id
        ).exists()
        if not assigned:
            raise ReviewerNotAssignedError("Ревьювер не назначен на этот pull request")

        reviewer_team = await TeamMember.filter(user_id=payload.old_user_id).first()
        if not reviewer_team:
            raise ReplacementCandidateNotFoundError("У ревьювера нет команды")

        current_reviewer_ids = await PullRequestReviewer.filter(pr_id=pr_id).values_list(
            "reviewer_id", flat=True
        )

        candidate = await PullRequestReviewerService.pick_replacement_candidate(
            team_id=reviewer_team.team_id,
            exclude_ids=set(current_reviewer_ids) | {payload.old_user_id, pr.author_id},
        )

        if not candidate:
            raise ReplacementCandidateNotFoundError("Нет доступных кандидатов в команде ревьювера")

        await PullRequestReviewer.filter(pr_id=pr_id, reviewer_id=payload.old_user_id).delete()
        await PullRequestReviewer.create(pr_id=pr_id, reviewer_id=candidate.id)

        return pr, candidate.id

    @staticmethod
    async def to_dto(pr: PullRequest) -> PullRequestDto:
        reviewer_map = await PullRequestService.get_reviewer_map([pr.id])
        merged_at = pr.merged_at
        if pr.status == PRStatus.MERGED and merged_at is None:
            merged_at = pr.updated_at
        return PullRequestDto(
            pull_request_id=pr.id,
            pull_request_name=pr.title,
            status=pr.status,
            author_id=pr.author_id,
            assigned_reviewers=reviewer_map.get(pr.id, []),
            created_at=pr.created_at,
            merged_at=merged_at,
        )

    @staticmethod
    async def to_dtos(prs: list[PullRequest]) -> list[PullRequestDto]:
        if not prs:
            return []

        reviewer_map = await PullRequestService.get_reviewer_map([pr.id for pr in prs])
        return [
            PullRequestDto(
                pull_request_id=pr.id,
                pull_request_name=pr.title,
                status=pr.status,
                author_id=pr.author_id,
                assigned_reviewers=reviewer_map.get(pr.id, []),
                created_at=pr.created_at,
                merged_at=(
                    pr.merged_at or (pr.updated_at if pr.status == PRStatus.MERGED else None)
                ),
            )
            for pr in prs
        ]

    @staticmethod
    async def get_reviewer_map(pr_ids: list[UUID]) -> dict[UUID, list[UUID]]:
        return await PullRequestReviewerService.get_pull_request_reviewer_ids_map(pr_ids)

    @staticmethod
    async def get_pull_requests_for_reviewer(user_id: UUID) -> list[PullRequest]:
        exists = await User.filter(id=user_id).exists()
        if not exists:
            raise UserNotFoundError(f"Пользователь с id {user_id} не найден")

        pr_ids = await PullRequestReviewer.filter(reviewer_id=user_id).values_list(
            "pr_id", flat=True
        )
        if not pr_ids:
            return []

        return await PullRequest.filter(id__in=pr_ids).order_by("created_at")

    @staticmethod
    async def to_short_dtos(prs: list[PullRequest]) -> list[PullRequestShort]:
        return [
            PullRequestShort(
                pull_request_id=pr.id,
                pull_request_name=pr.title,
                status=pr.status,
                author_id=pr.author_id,
            )
            for pr in prs
        ]
