import uuid

import pytest
from httpx import AsyncClient


async def create_team(api_client: AsyncClient, name: str, members: list[dict]) -> None:
    resp = await api_client.post("/api/v1/team/add", json={"team_name": name, "members": members})
    assert resp.status_code == 201


@pytest.mark.asyncio
async def test_pull_request_lifecycle_blocks_reassign_after_merge(api_client: AsyncClient):
    author_id = str(uuid.uuid4())
    reviewer_ids = [str(uuid.uuid4()), str(uuid.uuid4())]

    await create_team(
        api_client,
        "core",
        [
            {"user_id": author_id, "username": "author", "is_active": True},
            {"user_id": reviewer_ids[0], "username": "r1", "is_active": True},
            {"user_id": reviewer_ids[1], "username": "r2", "is_active": True},
        ],
    )

    pr_id = str(uuid.uuid4())
    create_resp = await api_client.post(
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

    merge_resp = await api_client.post("/api/v1/pullRequest/merge", json={"pull_request_id": pr_id})
    assert merge_resp.status_code == 200
    assert merge_resp.json()["pr"]["status"] == "MERGED"

    reassign_resp = await api_client.post(
        "/api/v1/pullRequest/reassign",
        json={"pull_request_id": pr_id, "old_user_id": pr_body["assigned_reviewers"][0]},
    )
    assert reassign_resp.status_code == 409
    assert reassign_resp.json()["error"]["code"] == "PR_MERGED"


@pytest.mark.asyncio
async def test_create_pull_request_requires_existing_author(api_client: AsyncClient):
    pr_id = str(uuid.uuid4())
    missing_author_id = str(uuid.uuid4())

    resp = await api_client.post(
        "/api/v1/pullRequest/create",
        json={
            "pull_request_id": pr_id,
            "pull_request_name": "Non existent author",
            "author_id": missing_author_id,
        },
    )

    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_reassign_requires_assigned_reviewer(api_client: AsyncClient):
    author_id = str(uuid.uuid4())
    reviewer_ids = [str(uuid.uuid4()) for _ in range(3)]

    await create_team(
        api_client,
        "api",
        [
            {"user_id": author_id, "username": "author", "is_active": True},
            {"user_id": reviewer_ids[0], "username": "r1", "is_active": True},
            {"user_id": reviewer_ids[1], "username": "r2", "is_active": True},
            {"user_id": reviewer_ids[2], "username": "r3", "is_active": True},
        ],
    )

    pr_id = str(uuid.uuid4())
    create_resp = await api_client.post(
        "/api/v1/pullRequest/create",
        json={
            "pull_request_id": pr_id,
            "pull_request_name": "Edge cases",
            "author_id": author_id,
        },
    )
    assigned_reviewers = set(create_resp.json()["pr"]["assigned_reviewers"])
    unassigned = next((rid for rid in reviewer_ids if rid not in assigned_reviewers), None)
    assert unassigned is not None, "Expected at least one reviewer to remain unassigned"

    resp = await api_client.post(
        "/api/v1/pullRequest/reassign",
        json={"pull_request_id": pr_id, "old_user_id": unassigned},
    )

    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "NOT_ASSIGNED"


@pytest.mark.asyncio
async def test_reassign_replaces_reviewer_from_same_team(api_client: AsyncClient):
    author_id = str(uuid.uuid4())
    reviewer_ids = [str(uuid.uuid4()) for _ in range(3)]

    await create_team(
        api_client,
        "mobile",
        [
            {"user_id": author_id, "username": "author", "is_active": True},
            {"user_id": reviewer_ids[0], "username": "r1", "is_active": True},
            {"user_id": reviewer_ids[1], "username": "r2", "is_active": True},
            {"user_id": reviewer_ids[2], "username": "r3", "is_active": True},
        ],
    )

    pr_id = str(uuid.uuid4())
    create_resp = await api_client.post(
        "/api/v1/pullRequest/create",
        json={
            "pull_request_id": pr_id,
            "pull_request_name": "Reassign flow",
            "author_id": author_id,
        },
    )
    assigned_reviewers = create_resp.json()["pr"]["assigned_reviewers"]
    assert len(assigned_reviewers) == 2

    old_reviewer = assigned_reviewers[0]
    reassign_resp = await api_client.post(
        "/api/v1/pullRequest/reassign",
        json={"pull_request_id": pr_id, "old_user_id": old_reviewer},
    )

    assert reassign_resp.status_code == 200
    body = reassign_resp.json()
    replacement = body["replaced_by"]
    new_reviewers = body["pr"]["assigned_reviewers"]

    assert replacement not in {author_id, old_reviewer}
    assert replacement in reviewer_ids
    assert len(new_reviewers) == 2
    assert old_reviewer not in new_reviewers
    assert replacement in new_reviewers
