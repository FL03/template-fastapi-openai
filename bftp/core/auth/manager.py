from passlib.context import CryptContext

from bftp.data.models.users import UserIn, Users


class Authenticator:
    username: str
    password: str

    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

    async def get_user(self):
        data = await UserIn.from_queryset_single(Users.get(username=self.username))
        return data

    async def verify(self, ctx: CryptContext):
        user = await self.get_user
        if user and ctx.verify(self.password, user.hashed_password):
            return user
