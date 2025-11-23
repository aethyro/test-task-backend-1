from app.common.errors.base import ServiceError


class UserError(ServiceError):
    default_message = "Произошла ошибка связанная с пользователем"
    default_code = "USER_ERROR"


class UserAlreadyExistsError(UserError):
    default_message = "Пользователь уже существует"
    default_code = "USER_EXISTS"


class UserNotFoundError(UserError):
    default_message = "Пользователь не найден"
    default_status_code = 404
    default_code = "NOT_FOUND"
