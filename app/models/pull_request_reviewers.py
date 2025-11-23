from tortoise import fields
from app.models.base import BaseModel


class PullRequestReviewer(BaseModel):
    pr = fields.ForeignKeyField(
        "models.PullRequest",
        on_delete=fields.CASCADE,
    )

    reviewer = fields.ForeignKeyField(
        "models.User",
        related_name="pr_reviews",
        on_delete=fields.CASCADE,
    )

    class Meta:
        table = "pull_request_reviewers"
        unique_together = ("pr", "reviewer")
