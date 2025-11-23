import logging

from tortoise import Tortoise

from app.core.config import Settings

logger = logging.getLogger(__name__)


async def init_db(settings: Settings) -> None:
    try:
        await Tortoise.init(
            db_url=settings.db_dsn,
            modules={"models": ["app.models"]},
        )
        logger.info("Tortoise ORM Инициализирована")
    except Exception:
        logger.exception("Ошибка инициализации Tortoise ORM")
        raise


async def close_db() -> None:
    try:
        await Tortoise.close_connections()
        logger.info("Соединение Tortoise ORM с базой закрыто")
    except Exception:
        logger.exception("Ошибка при закрытии соединений Tortoise ORM")


async def db_check() -> bool:
    try:
        conn = Tortoise.get_connection("default")
        await conn.execute_query("SELECT 1")
        return True
    except Exception:
        logger.exception("При попытке проверить подключение к базе произошла ошибка")
        return False
