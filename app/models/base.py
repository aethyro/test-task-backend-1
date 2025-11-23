import uuid

from tortoise import fields, models


class BaseModel(models.Model):
    id = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True
