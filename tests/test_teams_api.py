import uuid

import pytest
from httpx import AsyncClient

from app.models.teams import Team


@pytest.mark.asyncio
async def test_team_add_and_get(api_client: AsyncClient):
    team_payload = {
        "team_name": "backend",
        "members": [
            {"user_id": str(uuid.uuid4()), "username": "alice", "is_active": True},
            {"user_id": str(uuid.uuid4()), "username": "bob", "is_active": True},
        ],
    }

    create_resp = await api_client.post("/api/v1/team/add", json=team_payload)
    assert create_resp.status_code == 201
    body = create_resp.json()["team"]
    assert body["team_name"] == team_payload["team_name"]
    assert {m["username"] for m in body["members"]} == {"alice", "bob"}

    get_resp = await api_client.get(
        "/api/v1/team/get", params={"team_name": team_payload["team_name"]}
    )
    assert get_resp.status_code == 200
    assert get_resp.json()["team_name"] == team_payload["team_name"]


@pytest.mark.asyncio
async def test_team_add_duplicate_name_returns_conflict(api_client: AsyncClient):
    payload = {"team_name": "platform", "members": []}

    first_resp = await api_client.post("/api/v1/team/add", json=payload)
    assert first_resp.status_code == 201

    duplicate_resp = await api_client.post("/api/v1/team/add", json=payload)
    assert duplicate_resp.status_code == 400
    assert duplicate_resp.json()["error"]["code"] == "TEAM_EXISTS"


@pytest.mark.asyncio
async def test_add_team_members_requires_existing_users(api_client: AsyncClient):
    create_resp = await api_client.post("/api/v1/team/add", json={"team_name": "qa", "members": []})
    assert create_resp.status_code == 201

    team = await Team.filter(name="qa").first()
    assert team is not None

    missing_user_id = str(uuid.uuid4())
    resp = await api_client.post(
        f"/api/v1/team/{team.id}/members",
        json={"user_ids": [missing_user_id]},
    )

    assert resp.status_code == 404
    error = resp.json()["error"]
    assert error["code"] == "NOT_FOUND"
    assert missing_user_id in error["extra"]["user_ids"]


@pytest.mark.asyncio
async def test_delete_unknown_team_member_returns_not_found(api_client: AsyncClient):
    create_resp = await api_client.post(
        "/api/v1/team/add", json={"team_name": "sre", "members": []}
    )
    assert create_resp.status_code == 201

    team = await Team.filter(name="sre").first()
    assert team is not None

    orphan_member_id = str(uuid.uuid4())
    delete_resp = await api_client.delete(f"/api/v1/team/{team.id}/members/{orphan_member_id}")

    assert delete_resp.status_code == 404
    assert delete_resp.json()["error"]["code"] == "NOT_FOUND"
