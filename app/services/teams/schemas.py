from uuid import UUID

from pydantic import BaseModel, Field


class TeamMemberCreate(BaseModel):
    user_id: UUID
    username: str
    is_active: bool


class TeamMemberDto(BaseModel):
    user_id: UUID
    username: str
    is_active: bool


class TeamCreate(BaseModel):
    team_name: str = Field(min_length=2, max_length=150)
    members: list[TeamMemberCreate] = Field(default_factory=list)


class TeamMembersUpdate(BaseModel):
    user_ids: list[UUID] = Field(default_factory=list, min_length=1)


class TeamDto(BaseModel):
    team_name: str
    members: list[TeamMemberDto]

    model_config = {"from_attributes": True}


class TeamResponse(BaseModel):
    team: TeamDto
