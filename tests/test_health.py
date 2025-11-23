import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.core.config import get_settings
from app.db.tortoise import close_db, init_db
from app.main import create_app


@pytest_asyncio.fixture()
async def health_client(monkeypatch):
    monkeypatch.setenv("DB_SCHEME", "sqlite")
    monkeypatch.setenv("DB_DATABASE", ":memory:")
    monkeypatch.setenv("DB_USER", "")
    monkeypatch.setenv("DB_PASSWORD", "")
    monkeypatch.setenv("DB_HOST", "")
    monkeypatch.setenv("DB_PORT", "0")
    get_settings.cache_clear()
    app = create_app()
    settings = get_settings()
    await init_db(settings)
    app.state.app_initialized = True
    app.state.db_initialized = True

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    await close_db()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_healthz(health_client: AsyncClient):
    response = await health_client.get("/api/v1/health/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_handles_db_state(health_client: AsyncClient) -> None:
    response = await health_client.get("/api/v1/health/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "status" in body
    assert "dependencies" in body and "database" in body["dependencies"]
