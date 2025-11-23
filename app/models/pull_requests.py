from enum import Enum

from tortoise import fields

from app.models.base import BaseModel


class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class PullRequest(BaseModel):
    author = fields.ForeignKeyField(
        "models.User",
        related_name="authored_prs",
        null=True,
        on_delete=fields.SET_NULL,
    )

    status = fields.CharEnumField(PRStatus, max_length=50, default=PRStatus.OPEN)
    title = fields.CharField(max_length=255)

    class Meta:
        table = "pull_requests"
