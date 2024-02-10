import pymongo
from bson import Decimal128, ObjectId
from decimal import Decimal
from fastapi import HTTPException

from models import Transaction


client = pymongo.MongoClient("mongodb://spaghetti_db:27017")
db = client.spaghetti_db

users = db.users
users.create_index({"name": 1}, unique=True)

transactions = db.transactions
transactions.create_index({"source": 1, "date": 1})
transactions.create_index({"destination": 1, "date": 1})


def add_balance(user_id: str, amount: Decimal):
    result = users.update_one(
        {"_id": ObjectId(user_id)},
        {"$inc": {"balance": Decimal128(amount)}},
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=400, detail="invalid user id")


def add_transaction(source: str, destination: str, amount: Decimal, comment: str = "") -> Transaction:
    transaction = Transaction(id="", source=source, destination=destination, amount=amount, comment=comment)
    document: dict = transaction.model_dump(exclude={"id"})
    document["amount"] = Decimal128(document["amount"])
    result = transactions.insert_one(document)
    transaction.id = result.inserted_id.binary.hex()
    return transaction
