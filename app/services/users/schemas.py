from uuid import UUID

from pydantic import BaseModel, Field

from app.services.pull_requests.schemas import PullRequestShort


class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=150)


class UserSetIsActive(BaseModel):
    user_id: UUID
    is_active: bool


class UserDto(BaseModel):
    user_id: UUID
    username: str
    team_name: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    user: UserDto


class UserReviewsResponse(BaseModel):
    user_id: UUID
    pull_requests: list[PullRequestShort]
