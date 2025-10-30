import os
import hashlib
import hmac
from datetime import datetime, timedelta
from jose import JWTError, jwt
from config import PEPPER, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def hash_password(password: str, salt: str) -> str:
    hash_obj = hashlib.sha512()
    hash_obj.update(salt.encode() + password.encode() + PEPPER.encode())
    return hash_obj.hexdigest()

def verify_password(password: str, salt: str, stored_hash: str) -> bool:
    return hmac.compare_digest(stored_hash, hash_password(password, salt))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
