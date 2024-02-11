#!/usr/bin/env python3
import argparse
import secrets
from fastapi import HTTPException

import database


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("username", help="Username of the user to be created")
    parser.add_argument("password", help="Password of the user to be created", nargs="?", default=None)
    args = parser.parse_args()

    if args.password is None:
        args.password = secrets.token_urlsafe(16)
        print("[*] Password Generated:", args.password)

    try:
        user = database.create_user(args.username, args.password, admin=True)
        print("[*] User Access Token:", user.token)
    except HTTPException:
        print("[!] User already exists!")




if __name__ == '__main__':
    main()
