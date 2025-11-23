from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from app.db.tortoise import db_check

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/startup", status_code=status.HTTP_200_OK)
async def startup(request: Request) -> dict[str, str]:
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "not_ready"

    if request.app.state.app_initialized and request.app.state.db_initialized:
        status_code = status.HTTP_200_OK
        detail = "ok"

    body = {"status": detail}
    return JSONResponse(body, status_code=status_code)


@router.get("/healthz", status_code=status.HTTP_200_OK)
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def ready() -> JSONResponse:
    db_ok = await db_check()
    status_code = status.HTTP_200_OK if db_ok else status.HTTP_503_SERVICE_UNAVAILABLE
    body = {
        "status": "ready" if db_ok else "degraded",
        "dependencies": {"database": "ready" if db_ok else "unavailable"},
    }
    return JSONResponse(body, status_code=status_code)
