from tortoise import fields
from app.models.base import BaseModel


class TeamMember(BaseModel):
    team = fields.ForeignKeyField(
        "models.Team",
        on_delete=fields.CASCADE,
    )

    user = fields.ForeignKeyField(
        "models.User",
        related_name="team_memberships",
        on_delete=fields.CASCADE,
        unique=True,
    )

    class Meta:
        table = "team_members"
