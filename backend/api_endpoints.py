import secrets
from bson import ObjectId
from datetime import date, datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pymongo import ReturnDocument

import database
from dependencies import AuthorizedUser
from models import User, InviteCode, Transaction
from security import check_password, hash_password


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


class RegisterRequest(BaseModel):
    username: str
    password: str
    invite_code: str


@router.post("/register")
async def post_register(request: RegisterRequest):
    document = database.invite_codes.find_one({"code": request.invite_code})
    if document is None:
        raise HTTPException(status_code=401, detail="invalid invite code")
    code = InviteCode.from_mongo_document(document)
    if code.uses == 1:
        database.invite_codes.delete_one({"code": request.invite_code})
    elif code.uses != -1:
        database.invite_codes.update_one({"code": request.invite_code}, {"$inc": {"uses": -1}})

    user = User(id="", name=request.username, hashed_password=hash_password(request.password), balance=Decimal("25"))
    document = database.users.find_one_and_update(
        {"name": request.username},
        {"$set": user.model_dump(exclude={"id"})},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    user.id = document["_id"].binary.hex()

    return {
        "status": "success",
        "user": user.model_dump(exclude={"hashed_password"}),
        "token": user.token,
    }


@router.get("/invites")
async def get_all_invites(user: AuthorizedUser):
    if user.admin:
        documents = database.invite_codes.find({})
    else:
        documents = database.invite_codes.find({"creator": user.id})

    results = []
    for document in documents:
        invite = InviteCode.from_mongo_document(document)
        results.append(invite.model_dump(exclude={"id"}))

    return {"status": "success", "invites": results}


@router.get("/invite")
async def check_invite_code(code: str):
    document = database.invite_codes.find_one({"code": code})
    if document is None:
        raise HTTPException(status_code=400, detail="invalid invite code")
    return {"status": "success"}


@router.post("/invite")
async def create_invite_code(user: AuthorizedUser, uses: int = 1):
    generated_code = secrets.token_urlsafe(32)
    invite = InviteCode(id="", code=generated_code, creator=user.id, uses=uses)
    database.invite_codes.insert_one(invite.model_dump(exclude={"id"}))
    return {"status": "success", "code": generated_code}


@router.delete("/invite")
async def delete_invite_code(user: AuthorizedUser, code: str):
    document = database.invite_codes.find_one({"code": code})
    if document is None:
        raise HTTPException(status_code=400, detail="invalid invite code")
    invite = InviteCode.from_mongo_document(document)

    if invite.creator != user.id and not user.admin:
        raise HTTPException(status_code=403, detail="insufficient permission")

    database.invite_codes.delete_one({"code": code})
    return {"status": "success"}


@router.post("/friend")
async def add_friend(user: AuthorizedUser, name: str):
    friend = User.from_mongo_document(database.users.find_one({"name": name}))
    if friend.id == user.id:
        raise HTTPException(status_code=400, detail="cannot friend self")

    document = database.friendships.find_one({"source": user.id, "destination": friend.id})
    if document is not None:
        raise HTTPException(status_code=400, detail="already friends")

    database.friendships.insert_one({"source": user.id, "destination": friend.id})
    return {"status": "success"}


@router.get("/friends")
async def list_friends(user: AuthorizedUser):
    outbound = []
    for document in database.friendships.find({"source": user.id}):
        outbound.append(document["destination"])

    inbound = []
    for document in database.friendships.find({"destination": user.id}):
        inbound.append(document["source"])

    return {"status": "success", "outbound": outbound, "inbound": inbound}


@router.delete("/friend")
async def remove_friend(user: AuthorizedUser, name: str):
    friend = User.from_mongo_document(database.users.find_one({"name": name}))

    result = database.friendships.delete_one({"source": user.id, "destination": friend.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=400, detail="already not friends")

    return {"status": "success"}


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


@router.get("/user")
async def get_user_info(user: AuthorizedUser, user_id: str = None):
    if user_id is None:
        queried_user = user
    else:
        queried_user = User.from_mongo_document(database.users.find_one({"_id": ObjectId(user_id)}))
    return {"status": "success", "user": queried_user.model_dump(exclude={"hashed_password"})}


@router.get("/transactions")
async def get_transactions(user: AuthorizedUser, months_ago: int = 0):
    today = date.today()
    month = today.month
    year = today.year
    for _ in range(months_ago):
        month -= 1
        if month == 0:
            month = 12
            year -= 1

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    transactions: list[Transaction] = []

    outbound = database.transactions.find({
        "source": user.id,
        "date": {
            "$gte": datetime(year, month, 1),
            "$lt": datetime(next_year, next_month, 1)
        }
    })
    for document in outbound:
        transactions.append(Transaction.from_mongo_document(document))

    inbound = database.transactions.find({
        "destination": user.id,
        "date": {
            "$gte": datetime(year, month, 1),
            "$lt": datetime(next_year, next_month, 1)
        }
    })
    for document in inbound:
        transactions.append(Transaction.from_mongo_document(document))

    transactions.sort(key=lambda transaction: transaction.date)
    return {"status": "success", "transactions": transactions}