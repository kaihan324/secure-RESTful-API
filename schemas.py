from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class SensitiveDataIn(BaseModel):
    description: Optional[str]
    plaintext: str

class SensitiveDataOut(BaseModel):
    description: Optional[str]
    plaintext: str
