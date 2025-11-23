from uuid import UUID

from fastapi import APIRouter, Query, status

from app.services.team_members.team_members_service import TeamMemberService
from app.services.teams.schemas import (
    TeamCreate,
    TeamDto,
    TeamMembersUpdate,
    TeamResponse,
)
from app.services.teams.teams_service import TeamService

router = APIRouter(prefix="/team", tags=["Teams"])


@router.post(
    "/add",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать команду",
)
async def create_team(payload: TeamCreate) -> TeamResponse:
    team = await TeamService.create_team(payload)
    try:
        if payload.members:
            await TeamMemberService.update_or_create_members(team.id, payload.members)
    except Exception:
        await TeamService.delete_team(team.id)
        raise

    return TeamResponse(team=await TeamService.to_dto(team))


@router.get(
    "/get",
    response_model=TeamDto,
    status_code=status.HTTP_200_OK,
    summary="Получить команду по названию",
)
async def get_team_by_name(team_name: str = Query(..., alias="team_name")) -> TeamDto:
    team = await TeamService.get_team_by_name(team_name)
    return await TeamService.to_dto(team)


@router.get(
    "",
    response_model=list[TeamDto],
    status_code=status.HTTP_200_OK,
    summary="Получить все команды",
)
async def get_teams() -> list[TeamDto]:
    teams = await TeamService.get_teams()
    return await TeamService.to_dtos(teams)


@router.get(
    "/{team_id}",
    response_model=TeamDto,
    status_code=status.HTTP_200_OK,
    summary="Получить команду по id",
)
async def get_team(team_id: UUID) -> TeamDto:
    team = await TeamService.get_team(team_id)
    return await TeamService.to_dto(team)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить команду",
)
async def delete_team(team_id: UUID) -> None:
    await TeamService.delete_team(team_id)


@router.post(
    "/{team_id}/members",
    response_model=TeamDto,
    status_code=status.HTTP_200_OK,
    summary="Добавить участников в команду",
)
async def add_team_members(team_id: UUID, payload: TeamMembersUpdate) -> TeamDto:
    await TeamMemberService.add_team_members(team_id, payload.user_ids)
    team = await TeamService.get_team(team_id)
    return await TeamService.to_dto(team)


@router.delete(
    "/{team_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить участника из команды",
)
async def delete_team_member(team_id: UUID, user_id: UUID) -> None:
    await TeamMemberService.remove_team_member(team_id, user_id)
