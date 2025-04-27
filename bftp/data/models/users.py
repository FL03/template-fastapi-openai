from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator
from uuid import uuid4


class Users(Model):
    id = fields.CharField(max_length=128, null = False, pk=True, unique=True)
    email = fields.CharField(max_length=128, null=True, unique=True)
    hashed_password = fields.CharField(max_length=256, null=False)

    display_name = fields.CharField(max_length=128, null=True)
    username = fields.CharField(max_length=128, null=True)
    metadata = fields.JSONField(null=True)
    is_active = fields.BooleanField(default=True)

    prefix_name = fields.CharField(max_length=128, null=True)
    first_name = fields.CharField(max_length=128, null=True)
    middle_name = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128, null=True)
    suffix_name = fields.CharField(max_length=128, null=True)

    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.id:
            self.id = str(uuid4())

    def full_name(self):
        return " ".join(
            [
                i
                for i in [
                    self.prefix_name,
                    self.first_name,
                    self.middle_name,
                    self.last_name,
                    self.suffix_name,
                ]
                if i
            ]
        )

    class PydanticMeta:
        computed = ["full_name"]
        # exclude = ["hashed_password"]


User = pydantic_model_creator(Users, name="User")
UserIn = pydantic_model_creator(Users, exclude_readonly=True, name="UserIn")
