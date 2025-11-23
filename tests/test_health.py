import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthz(api_client: AsyncClient):
    response = await api_client.get("/api/v1/health/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_handles_db_state(api_client: AsyncClient) -> None:
    response = await api_client.get("/api/v1/health/ready")
    assert response.status_code in (200, 503)
    body = response.json()
    assert "status" in body
    assert "dependencies" in body and "database" in body["dependencies"]
