from fastapi import FastAPI
from functools import lru_cache
from tortoise import generate_config
from tortoise.contrib.fastapi import RegisterTortoise

from .auth import AuthSession, get_auth_session
from .settings import AppSettings, get_settings


class AppSession(object):
    credentials: list = []
    state: dict = {}
    auth: AuthSession
    settings: AppSettings = get_settings()

    def __init__(self, credentials = [], state = {}):
        self.credentials = credentials if credentials else []
        self.state = state if state else {}

        self.auth = AuthSession(secret_key=self.settings.secret_key)

    def info(self) -> dict:
        return dict(
            credentials=self.credentials,
            state=self.state,
            settings=self.settings,
        )



    async def register_orm(self, app: FastAPI, testing: bool = False):
        config = generate_config(
            self.settings.database_url,
            app_modules={"models": ["bftp.data.models"]},
            testing=testing,
            connection_label="models",
        )
        return await RegisterTortoise(
            app=app,
            config=config,
            add_exception_handlers=True,
            generate_schemas=True,
            _create_db=True,
        )


@lru_cache
def appSession() -> AppSession:
    return AppSession()
