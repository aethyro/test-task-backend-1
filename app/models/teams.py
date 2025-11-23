from tortoise import fields

from app.models.base import BaseModel


class Team(BaseModel):
    name = fields.CharField(max_length=150, unique=True)

    class Meta:
        table = "teams"
