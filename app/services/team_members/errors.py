from app.common.errors.base import ServiceError


class TeamMemberError(ServiceError):
    default_message = "Произошла ошибка связанная с участником команды"
