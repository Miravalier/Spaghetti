from decimal import Decimal
from fastapi import APIRouter
from pydantic import BaseModel

import database
from dependencies import AdminUser


router = APIRouter()


@router.get("/status")
async def get_status(admin: AdminUser):
    return {"status": "success", "user": admin.model_dump(exclude={"hashed_password"})}


class CreateUserRequest(BaseModel):
    username: str
    password: str
    admin: bool = False


@router.post("/user")
async def post_user(admin: AdminUser, request: CreateUserRequest):
    user = database.create_user(request.username, request.password, request.admin)
    return {
        "status": "success",
        "user": user.model_dump(exclude={"hashed_password"}),
    }


class GrantUserSpaghettiRequest(BaseModel):
    user_id: str
    amount: Decimal
    comment: str = ""


@router.post("/balance/grant")
async def grant_spaghetti(admin: AdminUser, request: GrantUserSpaghettiRequest):
    database.add_balance(request.user_id, request.amount)
    database.add_transaction("system", request.user_id, request.amount, request.comment)
    return {"status": "success"}
