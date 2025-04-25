from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.pydantic import pydantic_model_creator


class Tokens(Model):
    id = fields.IntField(pk=True)
    access_token = fields.CharField(max_length=256, null=False)
    token_type = fields.CharField(max_length=128, null=True)
    username = fields.CharField(max_length=128, null=True)

    class Meta:
        computed = []
        exclude = []


Token = pydantic_model_creator(Tokens, name="Token")
TokenIn = pydantic_model_creator(Tokens, exclude_readonly=True, name="TokenIn")
