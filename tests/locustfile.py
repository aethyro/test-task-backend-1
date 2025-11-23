import uuid

from locust import HttpUser, between, task


class ReviewerServiceUser(HttpUser):
    wait_time = between(0.1, 0.5)

    def on_start(self):
        self.author_id = str(uuid.uuid4())
        self.reviewer_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        self.team_name = f"team-{uuid.uuid4()}"

        payload = {
            "team_name": self.team_name,
            "members": [
                {"user_id": self.author_id, "username": "author", "is_active": True},
                {"user_id": self.reviewer_ids[0], "username": "r1", "is_active": True},
                {"user_id": self.reviewer_ids[1], "username": "r2", "is_active": True},
            ],
        }
        self.client.post("/api/v1/team/add", json=payload)

    @task(3)
    def health(self):
        self.client.get("/api/v1/health/healthz")

    @task(2)
    def create_and_merge_pr(self):
        pr_id = str(uuid.uuid4())
        create_payload = {
            "pull_request_id": pr_id,
            "pull_request_name": "feature-x",
            "author_id": self.author_id,
        }
        create_resp = self.client.post("/api/v1/pullRequest/create", json=create_payload)

        if create_resp.status_code == 201:
            self.client.post("/api/v1/pullRequest/merge", json={"pull_request_id": pr_id})

    @task(1)
    def get_reviews(self):
        if self.reviewer_ids:
            self.client.get(
                "/api/v1/users/getReview",
                params={"user_id": self.reviewer_ids[0]},
            )
