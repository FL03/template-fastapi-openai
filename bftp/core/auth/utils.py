from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from typing import Union

from bftp.data.models.users import User, Users


async def verify_password_hash(
    raw: str, hashed: str, context: CryptContext
) -> bool:
    return context.verify(raw, hashed)


async def get_user(username: str):
    data = await User.from_queryset_single(Users.get(username=username))
    if data:
        return data
    return None


async def validate_user_credentials(
    username: str, password: str, context: CryptContext
):
    user = await get_user(username)
    if user and verify_password_hash(password=password, hashed=user.hashed_password, context=context):
        return user


def create_access_token(
    secret_key: str,
    claims: dict = {},
    headers: dict = {},
    algorithm: str = "HS256",
    expires_delta: Union[timedelta, None] = None,
) -> str:
    # copy the claims to avoid modifying the original claims
    claims = claims.copy()
    # override the delta if provided
    if expires_delta:
        delta = expires_delta
    else:
        # set the default expiration time
        delta = timedelta(minutes=15)
    # set the expiration time in the claims
    claims.update({"exp": datetime.now(timezone.utc) + delta})
    return jwt.encode(
        claims=claims,
        algorithm=algorithm,
        headers=headers,
        key=secret_key,
    )
