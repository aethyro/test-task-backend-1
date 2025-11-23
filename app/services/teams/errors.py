from app.common.errors.base import ServiceError


class TeamError(ServiceError):
    default_message = "Произошла ошибка связанная с командой"
    default_code = "TEAM_ERROR"


class TeamAlreadyExistsError(TeamError):
    default_message = "Команда с таким названием уже существует"
    default_status_code = 400
    default_code = "TEAM_EXISTS"


class TeamNotFoundError(TeamError):
    default_message = "Команда не найдена"
    default_status_code = 404
    default_code = "NOT_FOUND"


class TeamMemberAlreadyExistsError(TeamError):
    default_message = "Участник уже состоит в команде"
    default_status_code = 409
    default_code = "TEAM_MEMBER_EXISTS"


class TeamMemberNotFoundError(TeamError):
    default_message = "Участник команды не найден"
    default_status_code = 404
    default_code = "NOT_FOUND"
