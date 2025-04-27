from fastapi import APIRouter, Depends, Form, HTTPException
from typing import List

from bftp.api.routes.auth import get_current_active_user, auth
from bftp.data.messages import Status
from bftp.data.models import User, Users

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=List[User])
async def get_users():
    return await User.from_queryset(Users.all())


@router.post("/user", response_model=User)
async def create_user(username: str = Form(), password: str = Form(), email: str = Form()):
    hashed_password = auth.hash_password(password)
    user_obj = await Users.create(
        **dict(username=username, hashed_password=hashed_password, email=email)
    )
    return await User.from_tortoise_orm(user_obj)


@router.get(
    "/user/{uid}",
    response_model=User,
)
async def get_user(uid: int):
    return await User.from_queryset_single(Users.get(id=uid))


@router.put(
    "/user/{uid}",
    response_model=User,
)
async def update_user(uid: int, user = Depends(get_current_active_user)):
    await Users.filter(id=uid).update(**user.dict(exclude_unset=True))
    return await User.from_queryset_single(Users.get(id=uid))


@router.delete(
    "/user/{uid}",
    response_model=Status,
)
async def delete_user(uid: str, usr = Depends(get_current_active_user)):
    deleted_count = await Users.filter(id=usr.id).delete()
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {uid} not found")
    return Status(message=f"Deleted user {uid}")
