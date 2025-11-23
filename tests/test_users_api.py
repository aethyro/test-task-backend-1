import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_user_and_toggle_active(api_client: AsyncClient):
    create_resp = await api_client.post("/api/v1/users", json={"username": "alice"})
    assert create_resp.status_code == 201
    user_id = create_resp.json()["user_id"]

    deactivate_resp = await api_client.post(
        "/api/v1/users/setIsActive",
        json={"user_id": user_id, "is_active": False},
    )
    assert deactivate_resp.status_code == 200
    assert deactivate_resp.json()["user"]["is_active"] is False

    get_resp = await api_client.get(f"/api/v1/users/{user_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_create_user_duplicate_username_returns_conflict(api_client: AsyncClient):
    payload = {"username": "duplicate_user"}

    first_resp = await api_client.post("/api/v1/users", json=payload)
    assert first_resp.status_code == 201

    duplicate_resp = await api_client.post("/api/v1/users", json=payload)
    assert duplicate_resp.status_code == 409
    assert duplicate_resp.json()["error"]["code"] == "USER_EXISTS"


@pytest.mark.asyncio
async def test_get_reviews_for_user_without_assignments_returns_empty(api_client: AsyncClient):
    user_resp = await api_client.post("/api/v1/users", json={"username": "lonely-reviewer"})
    user_id = user_resp.json()["user_id"]

    reviews_resp = await api_client.get("/api/v1/users/getReview", params={"user_id": user_id})
    assert reviews_resp.status_code == 200

    body = reviews_resp.json()
    assert body["user_id"] == user_id
    assert body["pull_requests"] == []
