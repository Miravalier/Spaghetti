import pymongo
from bson import Decimal128, ObjectId
from decimal import Decimal
from fastapi import HTTPException
from pymongo.errors import DuplicateKeyError

from models import User, Transaction
from security import hash_password


client = pymongo.MongoClient("mongodb://spaghetti_db:27017")
db = client.spaghetti_db

users = db.users
users.create_index({"name": 1}, unique=True)

transactions = db.transactions
transactions.create_index({"source": 1, "date": 1})
transactions.create_index({"destination": 1, "date": 1})

friendships = db.friendships
friendships.create_index({"source": 1, "destination": 1})
friendships.create_index({"source": 1})
friendships.create_index({"destination": 1})

invite_codes = db.invite_codes
invite_codes.create_index({"code": 1})


def create_user(name: str, password: str, admin: bool = False, balance: Decimal = Decimal("25")) -> User:
    user = User(_id="", name=name, hashed_password=hash_password(password), admin=admin, balance=balance)
    new_user_document = user.model_dump(exclude={"id"})
    new_user_document["balance"] = Decimal128(new_user_document["balance"])
    try:
        result = users.insert_one(new_user_document)
    except DuplicateKeyError:
        raise HTTPException(status_code=400, detail="username taken")
    user.id = result.inserted_id.binary.hex()
    return user


def set_password(user_id: str, password: str) -> bool:
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"hashed_password": hash_password(password)}},
    )
    return result.modified_count != 0


def add_balance(user_id: str, amount: Decimal):
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"balance": Decimal128(amount)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=400, detail="invalid user id")


def add_transaction(source: str, destination: str, amount: Decimal, comment: str = "") -> Transaction:
    transaction = Transaction(_id="", source=source, destination=destination, amount=amount, comment=comment)
    document: dict = transaction.model_dump(exclude={"id"})
    document["amount"] = Decimal128(document["amount"])
    result = transactions.insert_one(document)
    transaction.id = result.inserted_id.binary.hex()
    return transaction
