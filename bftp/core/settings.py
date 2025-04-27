from functools import lru_cache
from pydantic import BaseModel
from pydantic_settings import BaseSettings

import os


def database_uri(
    prefix: str = "postgresql+asyncpg",
    name: str = "bftp",
    password: str = "password",
    host: str = "localhost",
    port: int = 5432,
    user: str = "user",
) -> str:
    if prefix == "sqlite":
        return f"{prefix}:///{name}"
    return f"{prefix}://{user}:{password}@{host}:{port}/{name}"


class Database(BaseModel):
    database_url: str = "sqlite://:memory:"

    echo: bool = False

    def from_mode(self, stage: str = "development"):
        if "dev" in stage or "development" == stage:
            self.echo = True
        else:
            self.echo = False

    def load_env(self, **kwargs):
        self.database_driver = os.environ.get(
            "DATABASE_DRIVER", kwargs["database_driver"]
        )
        self.database_url = os.environ.get("DATABASE_URL", kwargs["database_url"])


class ExtendedDatabaseConfig(Database):
    database_driver: str = "sqlite"
    database_name: str = "bftp"
    database_password: str = "password"
    database_host: str = "localhost"
    database_port: int = 5432
    database_user: str = "user"

    def __init__(
        self,
        driver="sqlite3",
        name="bftp",
        password="password",
        host="localhost",
        port=5432,
        user="user",
    ):
        database_driver = os.environ.get("DATABASE_DRIVER", driver)
        database_name = os.environ.get("DATABASE_NAME", name)
        database_password = os.environ.get("DATABASE_PASSWORD", password)
        database_host = os.environ.get("DATABASE_HOST", host)
        database_port = int(os.environ.get("DATABASE_PORT", port))
        database_user = os.environ.get("DATABASE_USER", user)
        if database_driver == "sqlite":
            database_url = os.path.join(os.getcwd(), database_name)
        elif database_driver == "postgresql" or database_driver == "postgresql+asyncpg":
            database_url = database_uri(
                prefix="postgresql+asyncpg",
                name=database_name,
                password=database_password,
                host=database_host,
                port=database_port,
                user=database_user,
            )
        else:
            database_url = database_uri(
                prefix=database_driver,
                name=database_name,
                password=database_password,
                host=database_host,
                port=database_port,
                user=database_user,
            )
        super().__init__(
            database_driver=database_driver,
            database_name=database_name,
            database_password=database_password,
            database_host=database_host,
            database_port=database_port,
            database_user=database_user,
            database_url=database_url,
        )

    # try and load the object from the environment variables, defaulting to the passed kwargs
    def load_env(self, **kwargs):
        self.database_driver = os.environ.get("DATABASE_DRIVER", kwargs.database_driver)
        self.database_url = os.environ.get("DATABASE_URL", kwargs.database_url)
        self.database_name = os.environ.get("DATABASE_NAME", kwargs.database_name)
        self.database_password = os.environ.get(
            "DATABASE_PASSWORD", kwargs.database_password
        )
        self.database_host = os.environ.get("DATABASE_HOST", kwargs.database_host)
        self.database_port = int(os.environ.get("DATABASE_PORT", kwargs.database_port))
        self.database_user = os.environ.get("DATABASE_USER", kwargs.database_user)

    def to_uri(self) -> str:
        if self.database_driver == "sqlite":
            return f"{self.database_driver}:///{self.database_name}"
        elif (
            self.database_driver == "postgresql"
            or self.database_driver == "postgresql+asyncpg"
        ):
            return f"{self.database_driver}://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        elif self.database_driver == "mysql":
            return f"{self.database_driver}://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
        else:
            raise ValueError(f"Unsupported database driver: {self.database_driver}")


class Server(BaseModel):
    host: str
    port: int
    reload: bool

    def __init__(self, host="0.0.0.0", port=8080, reload=False):
        isDev = os.environ.get("APP_ENV", "development") == "development"
        host = os.environ.get("SERVER_HOST", host)
        port = int(os.environ.get("SERVER_PORT", port))
        reload = os.environ.get("SERVER_RELOAD", reload or isDev)

        super().__init__(host=host, port=port, reload=reload)

    def from_mode(self, stage: str = "development"):
        if "dev" in stage or "development" == stage:
            self.reload = True
        else:
            self.reload = False


class AppSettings(BaseSettings):
    app_env: str = "development"
    app_url: str = "http://localhost:8080"
    database_url: str = "sqlite://:memory:"
    # app
    public_key: str = "some_public_key"
    secret_key: str = "some-token"
    # systems
    database: ExtendedDatabaseConfig = ExtendedDatabaseConfig()
    server: Server = Server()
    # service providers
    openai_api_key: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(cls, init_settings, env_settings, file_secret_settings):
            return init_settings, env_settings, file_secret_settings


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
