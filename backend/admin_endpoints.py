from decimal import Decimal
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from pydantic import BaseModel

import database
from dependencies import AdminUser, verify_user


router = APIRouter()


@router.get("/status")
async def get_status(admin: AdminUser):
    return {"status": "success", "user": admin.model_dump(exclude={"hashed_password"})}


@router.post("/verification")
async def post_verification(admin: AdminUser, token: str):
    try:
        return {"status": "success", "user": verify_user(token)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail="verification failed")



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
