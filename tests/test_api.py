import os
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tortoise import Tortoise

from app.core.config import get_settings
from app.db.tortoise import close_db, init_db
from app.main import create_app


@pytest_asyncio.fixture()
async def client(monkeypatch):
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

    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        await Tortoise.generate_schemas()
        yield ac

    await close_db()
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_team_add_and_get(client: AsyncClient):
    team_payload = {
        "team_name": "backend",
        "members": [
            {
                "user_id": str(uuid.uuid4()),
                "username": "alice",
                "is_active": True,
            },
            {
                "user_id": str(uuid.uuid4()),
                "username": "bob",
                "is_active": True,
            },
        ],
    }

    create_resp = await client.post("/api/v1/team/add", json=team_payload)
    assert create_resp.status_code == 201
    body = create_resp.json()["team"]
    assert body["team_name"] == team_payload["team_name"]
    assert {m["username"] for m in body["members"]} == {"alice", "bob"}

    get_resp = await client.get("/api/v1/team/get", params={"team_name": team_payload["team_name"]})
    assert get_resp.status_code == 200
    assert get_resp.json()["team_name"] == team_payload["team_name"]


@pytest.mark.asyncio
async def test_pull_request_lifecycle(client: AsyncClient):
    author_id = str(uuid.uuid4())
    reviewer_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

    await client.post(
        "/api/v1/team/add",
        json={
            "team_name": "core",
            "members": [
                {
                    "user_id": author_id,
                    "username": "author",
                    "is_active": True,
                },
                {
                    "user_id": reviewer_ids[0],
                    "username": "r1",
                    "is_active": True,
                },
                {
                    "user_id": reviewer_ids[1],
                    "username": "r2",
                    "is_active": True,
                },
            ],
        },
    )

    pr_id = str(uuid.uuid4())
    create_resp = await client.post(
        "/api/v1/pullRequest/create",
        json={
            "pull_request_id": pr_id,
            "pull_request_name": "Add search",
            "author_id": author_id,
        },
    )
    assert create_resp.status_code == 201
    pr_body = create_resp.json()["pr"]
    assert pr_body["status"] == "OPEN"
    assert len(pr_body["assigned_reviewers"]) == 2
    assert author_id not in pr_body["assigned_reviewers"]

    merge_resp = await client.post("/api/v1/pullRequest/merge", json={"pull_request_id": pr_id})
    assert merge_resp.status_code == 200
    assert merge_resp.json()["pr"]["status"] == "MERGED"

    reassign_resp = await client.post(
        "/api/v1/pullRequest/reassign",
        json={
            "pull_request_id": pr_id,
            "old_user_id": pr_body["assigned_reviewers"][0],
        },
    )
    assert reassign_resp.status_code == 409
    assert reassign_resp.json()["error"]["code"] == "PR_MERGED"
