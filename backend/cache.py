from bson import ObjectId
from fastapi.exceptions import HTTPException

import database
from models import User


# TODO - time these entries out at some point
friends: dict[tuple[str,str], bool] = {}
user_names_by_id: dict[str, str] = {}


def lookup_user_name(user_id: str) -> str:
    if user_id == "system":
        return "System"

    user_name = user_names_by_id.get(user_id, None)
    if user_name is not None:
        return user_name

    user = User.from_mongo_document(database.users.find_one({"_id": ObjectId(user_id)}))
    user_names_by_id[user_id] = user.name
    return user.name


def store_user_name(user_id: str, user_name: str):
    user_names_by_id[user_id] = user_name


def are_friends(user_a: User, user_b: User) -> bool:
    result = friends.get((user_a.id, user_b.id), None)
    if result is not None:
        return result

    a_to_b = database.friendships.find_one({"source": user_a.id, "destination": user_b.id})
    b_to_a = database.friendships.find_one({"destination": user_a.id, "source": user_b.id})
    result = a_to_b is not None and b_to_a is not None
    friends[(user_a.id, user_b.id)] = result
    return result


def check_view_permission(viewing_user: User | None, viewed_user: User):
    if viewed_user.privacy == "public":
        return

    if viewing_user is not None:
        if viewing_user.admin or viewed_user is viewing_user:
            return

        if viewed_user.privacy == "friends" and are_friends(viewed_user, viewing_user):
            return

    raise HTTPException(status_code=403, detail="insufficient permission")
