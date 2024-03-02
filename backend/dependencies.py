import base64
import hashlib
from bson import ObjectId
from hmac import compare_digest
from fastapi import Depends, Header, HTTPException
from typing import Annotated

import database
from models import AuthObject, User
from settings import ADMIN_TOKEN


async def authorization_token(authorization: Annotated[str | None, Header()] = None, access_token: str | None = None) -> str:
    if authorization is not None and access_token is not None:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"}, detail="invalid authorization")

    if authorization is not None:
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"}, detail="invalid authorization")
        token = authorization[len("Bearer "):]

    elif access_token is not None:
        token = access_token

    else:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"}, detail="unauthorized")

    return token


AuthorizationToken = Annotated[str, Depends(authorization_token)]


async def verify_user(token: str) -> User:
    try:
        auth_object = AuthObject.model_validate_json(base64.b64decode(token))
    except:
        raise ValueError("invalid token contents")

    if not auth_object.auth:
        raise ValueError("incorrect token type")

    hash_string = ADMIN_TOKEN + auth_object.nonce + auth_object.user_id + "VERIFY"
    expected_signature = hashlib.sha512(hash_string.encode()).digest()
    given_signature = base64.b64decode(auth_object.signature)
    if not compare_digest(expected_signature, given_signature):
        raise ValueError("signature does not match")

    return User.from_mongo_document(database.users.find_one({"_id": ObjectId(auth_object.user_id)}))


async def authorized_user(token: AuthorizationToken) -> User:
    try:
        auth_object = AuthObject.model_validate_json(base64.b64decode(token))
    except:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"}, detail="invalid authorization")

    if not auth_object.auth:
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"}, detail="incorrect token type")

    hash_string = ADMIN_TOKEN + auth_object.nonce + auth_object.user_id + "AUTH"
    expected_signature = hashlib.sha512(hash_string.encode()).digest()
    given_signature = base64.b64decode(auth_object.signature)
    if not compare_digest(expected_signature, given_signature):
        raise HTTPException(status_code=401, headers={"WWW-Authenticate": "Bearer"}, detail="unauthorized")

    return User.from_mongo_document(database.users.find_one({"_id": ObjectId(auth_object.user_id)}))


AuthorizedUser = Annotated[User, Depends(authorized_user)]


async def admin_user(user: AuthorizedUser) -> User:
    if not user.admin:
        raise HTTPException(status_code=403, detail="insufficient permissions")

    return user


AdminUser = Annotated[User, Depends(admin_user)]
