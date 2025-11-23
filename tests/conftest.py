import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app.core.config import get_settings
from app.db.tortoise import close_db, init_db
from app.main import create_app


def prepare_sqlite_env(monkeypatch):
    monkeypatch.setenv("DB_SCHEME", "sqlite")
    monkeypatch.setenv("DB_DATABASE", ":memory:")
    monkeypatch.setenv("DB_USER", "")
    monkeypatch.setenv("DB_PASSWORD", "")
    monkeypatch.setenv("DB_HOST", "")
    monkeypatch.setenv("DB_PORT", "0")
    get_settings.cache_clear()


@pytest_asyncio.fixture()
async def api_client(monkeypatch):
    prepare_sqlite_env(monkeypatch)

    app = create_app()
    settings = get_settings()
    await init_db(settings)
    app.state.app_initialized = True
    app.state.db_initialized = True

    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await Tortoise.generate_schemas()
        yield client

    await close_db()
    get_settings.cache_clear()
