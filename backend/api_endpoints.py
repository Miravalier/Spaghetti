from decimal import Decimal
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


class TransferRequest(BaseModel):
    source: str
    destination: str
    amount: Decimal
    comment: str = ""


@router.post("/transfer")
async def post_transfer(user: AuthorizedUser, request: TransferRequest):
    if request.amount < 0:
        raise HTTPException(status_code=400, detail="negative amount is not allowed")

    if request.source == request.destination:
        raise HTTPException(status_code=400, detail="source and destination must be different")

    if user.id == request.source:
        if user.balance < request.amount:
            raise HTTPException(status_code=400, detail="insufficient funds")
        database.add_balance(request.destination, request.amount)
        database.add_balance(request.source, -request.amount)
        database.add_transaction(request.source, request.destination, request.amount, request.comment)
    elif user.id == request.destination:
        # TODO - request spaghetti from people
        raise HTTPException(status_code=400, detail="not yet implemented")
    else:
        raise HTTPException(status_code=400, detail="transfer does not involve you")

    return {"status": "success"}
