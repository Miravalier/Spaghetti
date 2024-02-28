from bson import ObjectId

import database
from models import User


user_names_by_id: dict[str, str] = {}


def lookup_user_name(user_id: str) -> str:
    user_name = user_names_by_id.get(user_id, None)
    if user_name is not None:
        return user_name

    user = User.from_mongo_document(database.users.find_one({"_id": ObjectId(user_id)}))
    user_names_by_id[user_id] = user.name
    return user.name


def store_user_name(user_id: str, user_name: str):
    user_names_by_id[user_id] = user_name
