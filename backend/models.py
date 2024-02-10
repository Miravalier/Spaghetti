import base64
import hashlib
import secrets
from pydantic import BaseModel

from settings import ADMIN_TOKEN


class User(BaseModel):
    id: str
    name: str
    hashed_password: bytes
    admin: bool = False

    @property
    def token(self) -> str:
        nonce = secrets.token_hex(8)
        signature = base64.b64encode(hashlib.sha512((ADMIN_TOKEN + nonce + self.id).encode()).digest()).decode()
        json_string = AuthObject(user_id=self.id, nonce=nonce, signature=signature).model_dump_json()
        return base64.b64encode(json_string.encode()).decode()


class AuthObject(BaseModel):
    user_id: str
    nonce: str
    signature: str
