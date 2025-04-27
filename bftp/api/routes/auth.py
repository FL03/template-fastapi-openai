from datetime import timedelta
from jose import JWTError, jwt
from pydantic import ValidationError
from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm, SecurityScopes
from typing import Annotated

from bftp.core import appSession
from bftp.core.auth import AccessToken, get_user, validate_user_credentials
from bftp.data.models.tokens import Token, Tokens

router = APIRouter(tags=["auth"])
session = appSession()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    formData: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    user = await validate_user_credentials(
        username=formData.username, password=formData.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = AccessToken(
        claims=dict(sub=user.username, scopes=formData.scopes),
        expires_delta=timedelta(minutes=session.auth.expires),
    ).encode(auth=session.auth.secret_key)
    return await Tokens.create(**dict(access_token=access_token, token_type="bearer"))


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(session.auth.scheme),
):
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(
            token, session.auth.secret_key, algorithms=[session.auth.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = Token(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_active_user(current_user=Security(get_current_user, scopes=[])):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
