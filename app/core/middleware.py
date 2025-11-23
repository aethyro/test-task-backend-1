import logging
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from app.common.errors.base import ServiceError

logger = logging.getLogger(__name__)


class ServiceErrorMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next) -> JSONResponse | Response:
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        try:
            response = await call_next(request)

        except ServiceError as exc:
            logger.warning(
                "ServiceError: %s %s -> %s (%s) extra=%s request_id=%s",
                request.method,
                request.url.path,
                exc.status_code,
                exc.message,
                exc.extra,
                request_id,
            )

            content = exc.to_dict()
            return JSONResponse(
                status_code=exc.status_code,
                content=jsonable_encoder(content),
                headers={"X-Request-ID": request_id},
            )

        except Exception:
            logger.exception(
                "Неожиданная ошибка %s %s request_id=%s",
                request.method,
                request.url.path,
                request_id,
            )

            content = {
                "error": {
                    "code": "SERVICE_ERROR",
                    "message": "Произошла ошибка",
                }
            }
            return JSONResponse(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                content=jsonable_encoder(content),
                headers={"X-Request-ID": request_id},
            )

        response.headers["X-Request-ID"] = request_id
        return response
