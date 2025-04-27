from datetime import datetime, timedelta, timezone
from jose import jwt
from pydantic import BaseModel
from typing import Union



class AccessToken(BaseModel):
    claims: dict
    headers: dict = {}
    algorithm: str = "HS256"
    expires_delta: Union[timedelta, None]
    jwt: str = None


    def encode(
        self,
        secret_key: str,
    ) -> str:
        # copy the claims to avoid modifying the original claims
        claims = self.claims.copy()
        # override the delta if provided
        if self.expires_delta:
            delta = self.expires_delta
        else:
            # set the default expiration time
            delta = timedelta(minutes=15)
        # set the expiration time in the claims
        claims.update({"exp": datetime.now(timezone.utc) + delta})
        self.jwt = jwt.encode(
            claims=claims,
            algorithm=self.algorithm,
            headers=self.headers,
            key=secret_key,
        )
        return self.jwt
