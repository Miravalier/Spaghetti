#!/usr/bin/env python3
import argparse
import secrets
from fastapi import HTTPException

import database
from models import User


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    create_parser = subparsers.add_parser("create-admin")
    create_parser.set_defaults(action="create-admin")
    create_parser.add_argument("username", help="Username of the user to be created")
    create_parser.add_argument("password", help="Password of the user to be created", nargs="?", default=None)

    reset_parser = subparsers.add_parser("reset-password")
    reset_parser.set_defaults(action="reset-password")
    reset_parser.add_argument("username", help="User whose password will be set")
    reset_parser.add_argument("password", help="Password to set")
    args = parser.parse_args()

    if args.action == "create-admin":
        if args.password is None:
            args.password = secrets.token_urlsafe(16)
            print("[*] Password Generated:", args.password)
        try:
            user = database.create_user(args.username, args.password, admin=True)
            print("[*] User Access Token:", user.token)
        except HTTPException:
            print("[!] User already exists!")
    elif args.action == "reset-password":
        try:
            user = User.from_mongo_document(database.users.find_one({"name": args.username}))
        except HTTPException:
            print(f"[!] User '{args.username}' does not exist")
        if database.set_password(user.id, args.password):
            print("[*] Password updated")
        else:
            print("[!] Failed to update password")




if __name__ == '__main__':
    main()
