import secrets
from bson import ObjectId
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

import database
from cache import lookup_user_name, check_view_permission
from dependencies import AuthorizedUser, AdminUser
from models import User, InviteCode, Transaction
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

    return {
        "status": "success",
        "user": user.model_dump(exclude={"hashed_password"}),
        "token": user.token,
    }


class RegisterRequest(BaseModel):
    username: str
    password: str
    invite_code: str


@router.post("/register")
async def post_register(request: RegisterRequest):
    document = database.invite_codes.find_one({"code": request.invite_code})
    if document is None:
        raise HTTPException(status_code=401, detail="invalid invite code")
    invite = InviteCode.from_mongo_document(document)

    user = database.create_user(request.username, request.password)

    # add friend invite.creator
    database.friendships.insert_one({"source": user.id, "destination": invite.creator})
    database.friendships.insert_one({"destination": user.id, "source": invite.creator})

    if invite.uses == 1:
        database.invite_codes.delete_one({"code": request.invite_code})
    elif invite.uses != -1:
        database.invite_codes.update_one({"code": request.invite_code}, {"$inc": {"uses": -1}})

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


class CreateInviteRequest(BaseModel):
    uses: int = 1


@router.post("/invite")
async def create_invite_code(user: AdminUser, request: CreateInviteRequest):
    generated_code = secrets.token_urlsafe(32)
    invite = InviteCode(_id="", code=generated_code, creator=user.id, uses=request.uses)
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


class AddFriendRequest(BaseModel):
    name: str


@router.post("/friend")
async def add_friend(user: AuthorizedUser, request: AddFriendRequest):
    document = database.users.find_one({"name": request.name})
    if document is None:
        raise HTTPException(status_code=400, detail=f"no user named '{request.name}'")
    friend = User.from_mongo_document(document)
    if friend.id == user.id:
        raise HTTPException(status_code=400, detail="cannot friend self")

    document = database.friendships.find_one({"source": user.id, "destination": friend.id})
    if document is not None:
        raise HTTPException(status_code=400, detail="already friends")

    database.friendships.insert_one({"source": user.id, "destination": friend.id})
    return {"status": "success"}


@router.get("/friends")
async def list_friends(user: AuthorizedUser):
    outbound = {}
    for document in database.friendships.find({"source": user.id}):
        outbound[document["destination"]] = lookup_user_name(document["destination"])

    inbound = {}
    for document in database.friendships.find({"destination": user.id}):
        inbound[document["source"]] = lookup_user_name(document["source"])

    return {"status": "success", "outbound": outbound, "inbound": inbound}


@router.delete("/friend")
async def remove_friend(user: AuthorizedUser, name: str):
    friend = User.from_mongo_document(database.users.find_one({"name": name}))

    result = database.friendships.delete_one({"source": user.id, "destination": friend.id})
    deleted_count = result.deleted_count

    result = database.friendships.delete_one({"destination": user.id, "source": friend.id})
    deleted_count += result.deleted_count

    if deleted_count == 0:
        raise HTTPException(status_code=400, detail="already not friends")
    elif deleted_count == 1:
        detail = "deleted friend request"
    else:
        detail = "removed friend"

    return {"status": "success", "detail": detail}


class TransferRequest(BaseModel):
    source: str
    destination: str
    amount: Decimal
    comment: str = ""


@router.post("/transfer")
async def post_transfer(user: AuthorizedUser, request: TransferRequest):
    if request.amount < Decimal(1):
        raise HTTPException(status_code=400, detail="you must send at least 1 spaghetti")

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
async def get_user_info(user: AuthorizedUser, id: str = None, name: str = None):
    if id is not None and name is not None:
        raise HTTPException(status_code=400, detail="use either id or name")
    elif id is not None:
        queried_user = User.from_mongo_document(database.users.find_one({"_id": ObjectId(id)}))
    elif name is not None:
        document = database.users.find_one({"name": name})
        if document is None:
            raise HTTPException(status_code=400, detail="invalid username")
        queried_user = User.from_mongo_document(document)
    else:
        queried_user = user

    check_view_permission(user, queried_user)

    return {"status": "success", "user": queried_user.model_dump(exclude={"hashed_password"})}



class Privacy(str, Enum):
    public = "public"
    friends = "friends"
    private = "private"


class Settings(BaseModel):
    privacy: Privacy = None


@router.put("/user/settings")
async def update_user_settings(user: AuthorizedUser, settings: Settings):
    database.users.update_one(
        {"_id": ObjectId(user.id)},
        {"$set": settings.model_dump(exclude_none=True)},
    )


@router.get("/transactions")
async def get_transactions(user: AuthorizedUser, months_ago: int = 0, id: str = None):
    # Figure out date range
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

    # Check for user viewing permission
    if id is not None:
        queried_user = User.from_mongo_document(database.users.find_one({"_id": ObjectId(id)}))
    else:
        queried_user = user
    check_view_permission(user, queried_user)

    # Query transactions
    transactions: list[Transaction] = []

    outbound = database.transactions.find({
        "source": queried_user.id,
        "date": {
            "$gte": datetime(year, month, 1),
            "$lt": datetime(next_year, next_month, 1)
        }
    })
    for document in outbound:
        transactions.append(Transaction.from_mongo_document(document))

    inbound = database.transactions.find({
        "destination": queried_user.id,
        "date": {
            "$gte": datetime(year, month, 1),
            "$lt": datetime(next_year, next_month, 1)
        }
    })
    for document in inbound:
        transactions.append(Transaction.from_mongo_document(document))

    transactions.sort(key=lambda transaction: transaction.date)
    return {
        "status": "success",
        "transactions": [
            {
                "id": transaction,
                "date": transaction.date,
                "amount": transaction.amount,
                "comment": transaction.comment,
                "destination": transaction.destination,
                "destinationName": lookup_user_name(transaction.destination),
                "source": transaction.source,
                "sourceName": lookup_user_name(transaction.source),
            }
            for transaction in transactions
        ]
    }
