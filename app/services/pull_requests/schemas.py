from datetime import datetime
from uuid import UUID

from pydantic import AliasChoices, BaseModel, Field

from app.models.pull_requests import PRStatus


class PullRequestCreate(BaseModel):
    pull_request_id: UUID
    pull_request_name: str = Field(min_length=1, max_length=255)
    author_id: UUID


class PullRequestReassign(BaseModel):
    pull_request_id: UUID
    old_user_id: UUID = Field(validation_alias=AliasChoices("old_user_id", "old_reviewer_id"))

    model_config = {"populate_by_name": True}


class PullRequestMerge(BaseModel):
    pull_request_id: UUID


class PullRequestDto(BaseModel):
    pull_request_id: UUID
    pull_request_name: str
    author_id: UUID
    status: PRStatus
    assigned_reviewers: list[UUID]
    created_at: datetime | None = Field(None, alias="createdAt")
    merged_at: datetime | None = Field(None, alias="mergedAt")

    model_config = {
        "use_enum_values": True,
        "from_attributes": True,
        "populate_by_name": True,
    }


class PullRequestShort(BaseModel):
    pull_request_id: UUID
    pull_request_name: str
    author_id: UUID
    status: PRStatus

    model_config = {
        "use_enum_values": True,
        "from_attributes": True,
    }


class PullRequestResponse(BaseModel):
    pr: PullRequestDto


class PullRequestReassignResponse(BaseModel):
    pr: PullRequestDto
    replaced_by: UUID
