from uuid import UUID

from tortoise.exceptions import IntegrityError

from app.models.teams import Team
from app.services.team_members.team_members_service import TeamMemberService
from app.services.teams.errors import TeamAlreadyExistsError, TeamNotFoundError
from app.services.teams.schemas import TeamCreate, TeamDto, TeamMemberDto


class TeamService:
    @staticmethod
    async def create_team(payload: TeamCreate) -> Team:
        try:
            team = await Team.create(name=payload.team_name)
        except IntegrityError as exc:
            raise TeamAlreadyExistsError(
                f"Команда с названием {payload.team_name} уже существует",
                status_code=400,
            ) from exc

        return team

    @staticmethod
    async def get_team_by_name(name: str) -> Team:
        team = await Team.filter(name=name).first()
        if not team:
            raise TeamNotFoundError(f"Команда с названием {name} не найдена")
        return team

    @staticmethod
    async def to_dto(team: Team) -> TeamDto:
        members = await TeamMemberService.get_team_members(team.id)
        return TeamService.build_team_dto(team, members)

    @staticmethod
    async def to_dtos(teams: list[Team]) -> list[TeamDto]:
        if not teams:
            return []

        members_map = await TeamMemberService.get_team_members_map([team.id for team in teams])
        return [TeamService.build_team_dto(team, members_map.get(team.id, [])) for team in teams]

    @staticmethod
    def build_team_dto(team: Team, members) -> TeamDto:
        return TeamDto(
            team_name=team.name,
            members=[
                TeamMemberDto(
                    user_id=member.user.id,
                    username=member.user.username,
                    is_active=member.user.is_active,
                )
                for member in members
                if member.user is not None
            ],
        )

    @staticmethod
    async def get_team(team_id: UUID) -> Team:
        team = await Team.filter(id=team_id).first()
        if not team:
            raise TeamNotFoundError(f"Команда с id {team_id} не найдена")
        return team

    @staticmethod
    async def get_teams() -> list[Team]:
        return await Team.all()

    @staticmethod
    async def delete_team(team_id: UUID) -> None:
        deleted = await Team.filter(id=team_id).delete()
        if not deleted:
            raise TeamNotFoundError(f"Команда с id {team_id} не найдена")
