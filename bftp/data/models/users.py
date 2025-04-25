from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator


class Users(Model):
    id = fields.IntField(pk=True)
    prefix_name = fields.CharField(max_length=128, null=True)
    first_name = fields.CharField(max_length=128, null=True)
    middle_name = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128, null=True)
    suffix_name = fields.CharField(max_length=128, null=True)
    ensname = fields.CharField(max_length=128, null=True)
    hashed_password = fields.CharField(max_length=256, null=False)
    username = fields.CharField(max_length=128, null=True)

    created = fields.DatetimeField(auto_now_add=True)
    modified = fields.DatetimeField(auto_now=True)

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
