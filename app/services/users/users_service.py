from uuid import UUID

from tortoise.exceptions import IntegrityError

from app.models.team_members import TeamMember
from app.models.users import User
from app.services.users.errors import UserAlreadyExistsError, UserNotFoundError
from app.services.users.schemas import UserCreate, UserDto, UserSetIsActive


class UserService:
    @staticmethod
    async def set_user_is_active(payload: UserSetIsActive) -> User:
        user = await User.filter(id=payload.user_id).first()
        if not user:
            raise UserNotFoundError(f"Пользователь с id {payload.user_id} не найден")
        user.is_active = payload.is_active
        await user.save()
        return user

    @staticmethod
    async def create_user(payload: UserCreate) -> User:
        try:
            return await User.create(username=payload.username)
        except IntegrityError as exc:
            raise UserAlreadyExistsError(
                f"Пользователь с логином {payload.username} уже существует",
                status_code=409,
            ) from exc

    @staticmethod
    async def get_user(user_id: UUID) -> User:
        user = await User.filter(id=user_id).first()
        if not user:
            raise UserNotFoundError(f"Пользователь с id {user_id} не найден")
        return user

    @staticmethod
    async def delete_user(user_id: UUID) -> None:
        deleted_count = await User.filter(id=user_id).delete()
        if not deleted_count:
            raise UserNotFoundError(f"Пользователь с id {user_id} не найден")

    @staticmethod
    async def get_users() -> list[User]:
        return await User.all()

    @staticmethod
    async def get_team_name_map(user_ids: list[UUID]) -> dict[UUID, str | None]:
        if not user_ids:
            return {}

        mapping: dict[UUID, str | None] = {user_id: None for user_id in user_ids}

        memberships = await TeamMember.filter(user_id__in=user_ids).values_list(
            "user_id", "team__name"
        )

        for user_id, team_name in memberships:
            mapping[user_id] = team_name

        return mapping

    @staticmethod
    async def to_dto(user: User) -> UserDto:
        team_map = await UserService.get_team_name_map([user.id])
        return UserDto(
            user_id=user.id,
            username=user.username,
            is_active=user.is_active,
            team_name=team_map.get(user.id),
        )

    @staticmethod
    async def to_dtos(users: list[User]) -> list[UserDto]:
        if not users:
            return []

        team_map = await UserService.get_team_name_map([user.id for user in users])
        return [
            UserDto(
                user_id=user.id,
                username=user.username,
                is_active=user.is_active,
                team_name=team_map.get(user.id),
            )
            for user in users
        ]
