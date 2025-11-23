from tortoise import fields
from app.models.base import BaseModel
from app.models.pull_requests import PullRequest
from app.models.team_members import TeamMember
from app.models.pull_request_reviewers import PullRequestReviewer


class User(BaseModel):
    username = fields.CharField(max_length=150, unique=True)
    is_active = fields.BooleanField(default=True)

    authored_prs: fields.ReverseRelation["PullRequest"]
    team_memberships: fields.ReverseRelation["TeamMember"]
    pr_reviews: fields.ReverseRelation["PullRequestReviewer"]

    class Meta:
        table = "users"
