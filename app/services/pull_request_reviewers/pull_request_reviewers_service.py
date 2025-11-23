from uuid import UUID

from app.models.pull_request_reviewers import PullRequestReviewer
from app.models.pull_requests import PullRequest
from app.models.team_members import TeamMember
from app.models.users import User
from app.services.pull_requests.errors import PullRequestNotFoundError


class PullRequestReviewerService:
    @staticmethod
    async def add_pull_request_reviewers(
        pr_id: UUID, team_id: UUID, author_id: UUID, reviewer_count=2
    ) -> None:
        pr = await PullRequest.filter(id=pr_id).first()
        if not pr:
            raise PullRequestNotFoundError(f"Pull request с id {pr_id} не найден")

        candidates = await PullRequestReviewerService._get_candidates(
            team_id=team_id,
            reviewer_count=reviewer_count,
            exclude_ids={author_id},
        )

        if candidates:
            await PullRequestReviewer.bulk_create(
                [
                    PullRequestReviewer(pr_id=pr_id, reviewer_id=candidate.id)
                    for candidate in candidates
                ]
            )

    @staticmethod
    async def pick_replacement_candidate(team_id: UUID, exclude_ids: set[UUID]) -> User | None:
        candidates = await PullRequestReviewerService._get_candidates(
            team_id=team_id,
            reviewer_count=1,
            exclude_ids=exclude_ids,
        )
        if not candidates:
            return None
        return candidates[0]

    @staticmethod
    async def get_pull_request_reviewer_ids_map(
        pr_ids: list[UUID],
    ) -> dict[UUID, list[UUID]]:
        if not pr_ids:
            return {}

        reviewers = await PullRequestReviewer.filter(pr_id__in=pr_ids).values_list(
            "pr_id", "reviewer_id"
        )

        mapping: dict[UUID, list[UUID]] = {}
        for pr_id, reviewer_id in reviewers:
            mapping.setdefault(pr_id, []).append(reviewer_id)
        return mapping

    @staticmethod
    async def _get_candidates(
        team_id: UUID, reviewer_count: int, exclude_ids: set[UUID]
    ) -> list[User]:
        if reviewer_count <= 0:
            return []

        candidate_ids = await TeamMember.filter(team_id=team_id).values_list("user_id", flat=True)
        if not candidate_ids:
            return []

        return (
            await User.filter(id__in=candidate_ids, is_active=True)
            .exclude(id__in=list(exclude_ids))
            .order_by("id")
            .limit(reviewer_count)
        )
