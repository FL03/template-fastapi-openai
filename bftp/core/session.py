
from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from passlib.context import CryptContext
from pydantic import BaseModel

from .settings import Settings, settings


class Authorization(object):
    context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    scopes: dict = {"items": "View user items"}

    def __init__(
        self,
        algorithm: str = "HS256",
        endpoint: str = "/token",
        expires: int = 30,
        **kwargs
    ):
        self.algorithm: str = algorithm
        self.endpoint: str = endpoint
        self.expires: int = expires
        self.scopes = {**self.scopes, **kwargs}
        self.scheme = self.set_scheme()

    def set_scheme(self):
        return OAuth2PasswordBearer(tokenUrl=self.endpoint, scopes=self.scopes)

    def hash_password(self, password: str):
        return self.context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str):
        return self.context.verify(plain_password, hashed_password)


class Session(BaseModel):
    credentials: list = []
    state: dict = {}
    settings: Settings = settings()

    def info(self):
        return self.dict()


@lru_cache
def session() -> Session:
    return Session()
