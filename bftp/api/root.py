from fastapi import APIRouter, Depends
from bftp.api.routes import auth, oai, users

from bftp.api.routes.auth import get_current_active_user

v1 = APIRouter(tags=["v1"])
v1.include_router(router=auth.router)
v1.include_router(
    router=oai.router, dependencies=[Depends(get_current_active_user)]
)
v1.include_router(router=users.router)
