from fastapi import APIRouter
from pydantic import BaseModel
from pymongo import ReturnDocument

import database
from dependencies import AdminUser
from models import User
from security import hash_password


router = APIRouter()


@router.get("/status")
async def get_status(admin: AdminUser):
    return {"status": "success", "admin": admin.model_dump(exclude={"hashed_password"})}


class CreateUserRequest(BaseModel):
    username: str
    password: str
    admin: bool = False


@router.post("/user")
async def post_user(admin: AdminUser, request: CreateUserRequest):
    user = User(id="", name=request.username, hashed_password=hash_password(request.password), admin=request.admin)
    document = database.users.find_one_and_update(
        {"name": request.username},
        {"$set": user.model_dump(exclude={"id"})},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    user.id = document["_id"].binary.hex()

    return {
        "status": "success",
        "admin": admin.model_dump(exclude={"hashed_password"}),
        "user": user.model_dump(exclude={"hashed_password"}),
    }
