from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import database
from dependencies import AuthorizedUser
from models import User
from security import check_password


router = APIRouter()


@router.get("/status")
async def get_status(user: AuthorizedUser):
    return {"status": "success", "user": user.model_dump(exclude={"hashed_password"})}


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def post_login(request: LoginRequest):
    document = database.users.find_one({"name": request.username})
    if document is None:
        raise HTTPException(status_code=401, detail="invalid username or password")

    user = User.from_mongo_document(document)
    if not check_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="invalid username or password")

    return {"status": "success", "token": user.token}
