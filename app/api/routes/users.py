from uuid import UUID

from fastapi import APIRouter, Query, status

from app.services.pull_requests.pull_requests_service import PullRequestService
from app.services.users.schemas import (
    UserCreate,
    UserDto,
    UserResponse,
    UserReviewsResponse,
    UserSetIsActive,
)
from app.services.users.users_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "/setIsActive",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Установить флаг активности пользователя",
)
async def set_user_is_active(payload: UserSetIsActive) -> UserResponse:
    user = await UserService.set_user_is_active(payload)
    return UserResponse(user=await UserService.to_dto(user))


@router.get(
    "/getReview",
    response_model=UserReviewsResponse,
    status_code=status.HTTP_200_OK,
    summary="Получить PR, где пользователь ревьювер",
)
async def get_user_reviews(
    user_id: UUID = Query(..., alias="user_id"),
) -> UserReviewsResponse:
    prs = await PullRequestService.get_pull_requests_for_reviewer(user_id)
    return UserReviewsResponse(
        user_id=user_id,
        pull_requests=await PullRequestService.to_short_dtos(prs),
    )


@router.post(
    "",
    response_model=UserDto,
    status_code=status.HTTP_201_CREATED,
    summary="Создать пользователя",
)
async def create_user(payload: UserCreate) -> UserDto:
    user = await UserService.create_user(payload)
    return await UserService.to_dto(user)


@router.get(
    "/{user_id}",
    response_model=UserDto,
    status_code=status.HTTP_200_OK,
    summary="Получить пользователя по id",
)
async def get_user(user_id: UUID) -> UserDto:
    user = await UserService.get_user(user_id)
    return await UserService.to_dto(user)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получить всех пользователей",
)
async def get_users() -> list[UserDto]:
    users = await UserService.get_users()
    return await UserService.to_dtos(users)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить пользователя по id",
)
async def delete_user(user_id: UUID) -> None:
    await UserService.delete_user(user_id)
