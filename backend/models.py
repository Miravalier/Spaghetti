from __future__ import annotations

import base64
import hashlib
import secrets
from bson import Decimal128
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from pydantic.functional_validators import BeforeValidator
from typing import Annotated, Any, TypeVar, Type

from settings import ADMIN_TOKEN


def convert_decimal128_to_decimal(v: Any) -> Any:
    if isinstance(v, Decimal128):
        return v.to_decimal()
    return v


FlexibleDecimal = Annotated[Decimal, BeforeValidator(convert_decimal128_to_decimal)]


T = TypeVar('T', bound="MongoModel")


class MongoModel(BaseModel):
    @classmethod
    def from_mongo_document(cls: Type[T], document: dict) -> T:
        return cls.model_validate({
            ("id" if k == "_id" else k): (v.binary.hex() if k == "_id" else v)
            for k, v in document.items()
        })


class User(MongoModel):
    id: str
    name: str
    hashed_password: bytes
    admin: bool = False
    balance: FlexibleDecimal = Decimal()

    @property
    def token(self) -> str:
        nonce = secrets.token_hex(8)
        signature = base64.b64encode(hashlib.sha512((ADMIN_TOKEN + nonce + self.id).encode()).digest()).decode()
        json_string = AuthObject(user_id=self.id, nonce=nonce, signature=signature).model_dump_json()
        return base64.b64encode(json_string.encode()).decode()


class Transaction(MongoModel):
    id: str
    source: str
    destination: str
    amount: FlexibleDecimal
    date: datetime = Field(default_factory=datetime.now)
    comment: str = ""


class AuthObject(BaseModel):
    user_id: str
    nonce: str
    signature: str
