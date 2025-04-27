from fastapi.security import OAuth2PasswordBearer
from functools import lru_cache
from passlib.context import CryptContext

import os

from .token import AccessToken
from bftp.data.models.users import User, Users



class AuthSession(object):
    """
    AuthSession is a class that handles authentication and authorization for the application.
    """

    algorithm: str = "HS256"
    endpoint: str = "/token"
    expires: int = 30
    secret_key: str = "secret"
    scheme: OAuth2PasswordBearer = None
    context: CryptContext = CryptContext(schemes=["bcrypt"], deprecated="auto")
    scopes: dict = dict(items="View items the user has access to")

    def __init__(
        self,
        algorithm: str = "HS256",
        endpoint: str = "/token",
        expires: int = 30,
        secret_key: str = None,
        **kwargs,
    ):
        self.algorithm = algorithm
        self.endpoint = endpoint
        self.expires = expires

        self.set_scheme(kwargs.get("scopes"))
        self.secret_key = (
            secret_key if secret_key else os.getenv("SECRET_KEY", self.secret_key)
        )

    def set_scheme(self, scope: dict) -> OAuth2PasswordBearer:
        if scope:
            self.scopes = {**self.scopes, **scope}
        self.scheme = OAuth2PasswordBearer(tokenUrl=self.endpoint, scopes=self.scopes)
        return self.scheme

    # hash the input using the cryptographic engine
    def hash_password(self, password: str) -> str:
        return self.context.hash(password)

    # verify a password using the context and its hash
    def verify_password(self, raw: str, hash: str) -> bool:
        return self.context.verify(raw, hash)

    def create_access_token(
        self, data: dict, expires_delta: int = None
    ) -> str:
        """
        Create an access token using the secret key and algorithm.
        """
        if expires_delta:
            data.update({"exp": expires_delta})
        return AccessToken(
            claims=data, expires_delta=expires_delta
        ).create(auth=self)
    
    async def get_user(self, username: str):
        """
        Get a user from the database using the username.
        """
        data = await User.from_queryset_single(Users.get(username=username))
        if data:
            return data
        return None
# create and cache the AuthSession instance
@lru_cache
def get_auth_session() -> AuthSession:
    
    return AuthSession()
