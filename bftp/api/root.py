from fastapi import APIRouter, Depends
from bftp.api.routes import auth, oai, users

from bftp.api.routes.auth import get_current_active_user

# declare the root router for the API
api = APIRouter()
# inititialize the v1 router; 
v1 = APIRouter(tags=["v1"])
v1.include_router(
    router=oai.router, dependencies=[Depends(get_current_active_user)]
)
v1.include_router(router=users.router)
# include the auth route; exclude the auth route from the v1 router
api.include_router(router=auth.router, tags=["auth"])
# include the v1 router
api.include_router(router=v1, prefix="/v1", tags=["v1"])
