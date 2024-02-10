#!/usr/bin/env python3
import argparse
import secrets
from pymongo import ReturnDocument

import database
from models import User
from security import hash_password


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Username of the user to be created")
    parser.add_argument("password", help="Password of the user to be created", nargs="?", default=None)
    args = parser.parse_args()

    if args.password is None:
        args.password = secrets.token_urlsafe(16)
        print("[*] Password Generated:", args.password)

    user = User(id="", name=args.username, hashed_password=hash_password(args.password), admin=True)
    document = database.users.find_one_and_update(
        {"name": args.username},
        {"$set": user.model_dump(exclude={"id"})},
        upsert=True,
        return_document=ReturnDocument.AFTER
    )
    user.id = document["_id"].binary.hex()
    print("[*] User Access Token:", user.token)


if __name__ == '__main__':
    main()
