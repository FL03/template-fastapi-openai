import os
import tortoise
import uvicorn

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager


from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from tortoise.contrib.fastapi import (
    RegisterTortoise,
    tortoise_exception_handlers,
)

from bftp import core
from bftp.api.root import v1

session: core.Session = core.session()
settings: core.Settings = session.settings


@asynccontextmanager
async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
    config = tortoise.generate_config(
        os.getenv("DATABASE_URL", "sqlite://:memory:"),
        app_modules={"models": ["bftp.data.models"]},
        testing=True,
        connection_label="models",
    )
    async with RegisterTortoise(
        app=app,
        config=config,
        generate_schemas=True,
        _create_db=True,
    ):
        # db connected
        yield
        # app teardown
    # db connections closed
    tortoise.Tortoise._drop_databases()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if getattr(app.state, "testing", None):
        async with lifespan_test(app) as _:
            yield
    else:
        config = tortoise.generate_config(
            settings.database_url,
            app_modules={"models": ["bftp.data.models"]},
            testing=False,
            connection_label="models",
        )
        async with RegisterTortoise(
            app=app,
            config=config,
            add_exception_handlers=True,
            generate_schemas=True,
            _create_db=True,
        ):
            yield
            # app teardown
        # db connections closed
        await tortoise.Tortoise._drop_databases()


app: FastAPI = FastAPI(
    title="Restful", exception_handlers=tortoise_exception_handlers(), lifespan=lifespan
)

app.include_router(v1)


@lifespan("startup")
async def startup():
    print("Starting the application...")

    print("View the server locally at http://localhost:{}".format(settings.server.port))


@app.get("/")
async def homepage() -> RedirectResponse:
    return RedirectResponse("/docs")


@lifespan("shutdown")
async def shutdown():
    # Perform any cleanup tasks here
    tortoise.Tortoise.close_connections()
    print("Terminating the application...")


def run(host: str = "0.0.0.0", port=8080, reload=True):
    uvicorn.run("bftp.app:app", host=host, port=port, reload=reload)
