from app.common.errors.base import ServiceError


class PullRequestError(ServiceError):
    default_message = "Произошла ошибка связанная с pull request"
    default_code = "PR_ERROR"


class PullRequestNotFoundError(PullRequestError):
    default_message = "Pull request не найден"
    default_status_code = 404
    default_code = "NOT_FOUND"


class PullRequestAlreadyExistsError(PullRequestError):
    default_message = "Pull request уже существует"
    default_status_code = 409
    default_code = "PR_EXISTS"


class PullRequestMergedError(PullRequestError):
    default_message = "Нельзя изменить pull request в статусе MERGED"
    default_status_code = 409
    default_code = "PR_MERGED"


class ReviewerNotAssignedError(PullRequestError):
    default_message = "Пользователь не назначен ревьюером"
    default_status_code = 409
    default_code = "NOT_ASSIGNED"


class ReplacementCandidateNotFoundError(PullRequestError):
    default_message = "Нет доступных кандидатов для замены"
    default_status_code = 409
    default_code = "NO_CANDIDATE"
