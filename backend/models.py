from __future__ import annotations

import base64
import hashlib
import secrets
from bson import Decimal128, ObjectId
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, Any, TypeVar, Type

from settings import ADMIN_TOKEN


def convert_decimal128_to_decimal(v: Any) -> Any:
    if isinstance(v, Decimal128):
        return v.to_decimal()
    return v


def convert_mongo_id_to_str(v: Any) -> Any:
    if isinstance(v, ObjectId):
        return v.binary.hex()
    return v


FlexibleDecimal = Annotated[Decimal, BeforeValidator(convert_decimal128_to_decimal)]
MongoId = Annotated[str, Field(validation_alias="_id"), BeforeValidator(convert_mongo_id_to_str)]


T = TypeVar('T', bound="MongoModel")


class MongoModel(BaseModel):
    id: MongoId

    @classmethod
    def from_mongo_document(cls: Type[T], document: dict | None) -> T:
        if document is None:
            raise HTTPException(status_code=400, detail=f"invalid {cls.__name__} id")
        return cls.model_validate(document)


class InviteCode(MongoModel):
    code: str
    creator: str
    uses: int = 1
    date: datetime = Field(default_factory=datetime.now)


class User(MongoModel):
    name: str
    hashed_password: bytes
    admin: bool = False
    balance: FlexibleDecimal = Decimal()
    privacy: str = "private"

    @property
    def auth_token(self) -> str:
        nonce = secrets.token_hex(8)
        signature = base64.b64encode(hashlib.sha512((ADMIN_TOKEN + nonce + self.id + "AUTH").encode()).digest()).decode()
        json_string = AuthObject(user_id=self.id, nonce=nonce, auth=True, signature=signature).model_dump_json()
        return base64.b64encode(json_string.encode()).decode()

    @property
    def verification_token(self) -> str:
        nonce = secrets.token_hex(8)
        signature = base64.b64encode(hashlib.sha512((ADMIN_TOKEN + nonce + self.id + "VERIFY").encode()).digest()).decode()
        json_string = AuthObject(user_id=self.id, nonce=nonce, auth=False, signature=signature).model_dump_json()
        return base64.b64encode(json_string.encode()).decode()


class Transaction(MongoModel):
    source: str
    destination: str
    amount: FlexibleDecimal
    date: datetime = Field(default_factory=datetime.now)
    comment: str = ""


class AuthObject(BaseModel):
    user_id: str
    nonce: str
    auth: bool
    signature: str
