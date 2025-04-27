import tortoise
import uvicorn

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager


from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from tortoise.contrib.fastapi import tortoise_exception_handlers

from bftp.core import AppSession, AppSettings, appSession
from bftp.api import root

session: AppSession = appSession()
settings: AppSettings = session.settings

print("Loading the application...")
print("current session: {}", session.info())


@asynccontextmanager
async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
    async with await session.register_orm(app, testing=True) as _:
        # db connected
        yield
        # app teardown
    # db connections closed
    tortoise.Tortoise._drop_databases()


# lifespan is a context manager that handles the startup and shutdown of the application
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if getattr(app.state, "testing", None):
        async with lifespan_test(app) as _:
            yield
    else:
        async with await session.register_orm(app, testing=False) as _:
            yield
            # app teardown
        # db connections closed
        await tortoise.Tortoise._drop_databases()


# handle startup procedures
@lifespan("startup")
async def startup():
    print("Starting the application...")

    print("View the server locally at http://localhost:{}".format(settings.server.port))


# handle shutdown procudures
@lifespan("shutdown")
async def shutdown():
    # Perform any cleanup tasks here
    tortoise.Tortoise.close_connections()
    print("Terminating the application...")


# create the FastAPI app instance
app: FastAPI = FastAPI(
    exception_handlers=tortoise_exception_handlers(),
    lifespan=lifespan,
    description="A RESTful API built with FastAPI and Tortoise ORM.",
    title="BFTP",
)


# create a temporary directory root of the application
@app.get("/")
async def homepage() -> RedirectResponse:
    return RedirectResponse("/docs")


# include the base router
app.include_router(root.api, prefix="/api", tags=["v1"])


def run(host: str = "0.0.0.0", port=8080, reload=True):
    uvicorn.run("bftp.app:app", host=host, port=port, reload=reload)
