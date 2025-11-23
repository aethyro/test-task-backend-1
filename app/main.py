import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from app.api.routes.top import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import ServiceErrorMiddleware
from app.db.tortoise import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    logger = logging.getLogger(__name__)

    app.state.app_initialized = False
    app.state.db_initialized = False

    configure_logging(settings)

    logger.info("Запуск приложения...")
    try:
        await init_db(settings)
        app.state.db_initialized = True
        logger.info("База данных подключена")
    except Exception:
        logger.exception("Ошибка подключения базы данных")

    app.state.app_initialized = True

    yield

    app.state.app_initialized = False

    await close_db()
    app.state.db_initialized = False


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        debug=settings.debug,
        lifespan=lifespan,
    )

    app.include_router(api_router, prefix="/api/v1")
    app.add_middleware(ServiceErrorMiddleware)

    return app


app = create_app()
