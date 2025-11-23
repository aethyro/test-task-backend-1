from uuid import UUID

from app.models.team_members import TeamMember
from app.models.teams import Team
from app.models.users import User
from app.services.teams.errors import (
    TeamMemberAlreadyExistsError,
    TeamMemberNotFoundError,
    TeamNotFoundError,
)
from app.services.teams.schemas import TeamMemberCreate
from app.services.users.errors import UserNotFoundError


class TeamMemberService:
    @staticmethod
    async def add_team_member(team_id: UUID, user_id: UUID) -> None:
        await TeamMemberService.add_team_members(team_id, [user_id])

    @staticmethod
    async def add_team_members(team_id: UUID, user_ids: list[UUID]) -> None:
        user_ids = list(set(user_ids))

        team = await Team.filter(id=team_id).first()
        if not team:
            raise TeamNotFoundError(f"Команда с id {team_id} не найдена")

        users = await User.filter(id__in=user_ids)
        found_ids = {user.id for user in users}
        missing_ids = [uid for uid in user_ids if uid not in found_ids]
        if missing_ids:
            raise UserNotFoundError(
                f"Не найдены пользователи: {', '.join(map(str, missing_ids))}",
                status_code=404,
                extra={"user_ids": missing_ids},
            )

        existing_memberships = await TeamMember.filter(user_id__in=user_ids).values_list(
            "user_id", "team_id"
        )
        if existing_memberships:
            conflicting_user_ids = [user_id for user_id, _ in existing_memberships]
            raise TeamMemberAlreadyExistsError(
                "Пользователь уже состоит в команде",
                status_code=409,
                extra={"user_ids": conflicting_user_ids},
            )

        await TeamMember.bulk_create(
            [TeamMember(team_id=team_id, user_id=user_id) for user_id in user_ids],
        )

    @staticmethod
    async def remove_team_member(team_id: UUID, user_id: UUID) -> None:
        team_exists = await Team.filter(id=team_id).exists()
        if not team_exists:
            raise TeamNotFoundError(f"Команда с id {team_id} не найдена")

        deleted = await TeamMember.filter(team_id=team_id, user_id=user_id).delete()
        if not deleted:
            raise TeamMemberNotFoundError(f"Участник с id {user_id} не найден в команде {team_id}")

    @staticmethod
    async def get_team_members(team_id: UUID) -> list[TeamMember]:
        return await TeamMember.filter(team_id=team_id).select_related("user")

    @staticmethod
    async def get_team_members_map(
        team_ids: list[UUID],
    ) -> dict[UUID, list[TeamMember]]:
        if not team_ids:
            return {}

        memberships = (
            await TeamMember.filter(team_id__in=list(team_ids))
            .select_related("user")
            .order_by("created_at")
        )

        mapping = {}
        for member in memberships:
            mapping.setdefault(member.team_id, []).append(member)
        return mapping

    @staticmethod
    async def update_or_create_members(team_id: UUID, members: list[TeamMemberCreate]) -> None:
        team = await Team.filter(id=team_id).first()
        if not team:
            raise TeamNotFoundError(f"Команда с id {team_id} не найдена")

        for member in members:
            user, _ = await User.update_or_create(
                id=member.user_id,
                defaults={
                    "username": member.username,
                    "is_active": member.is_active,
                },
            )

            await TeamMember.filter(user_id=user.id).delete()
            await TeamMember.get_or_create(team_id=team_id, user_id=user.id)
