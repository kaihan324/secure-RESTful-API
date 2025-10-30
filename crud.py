from sqlalchemy.orm import Session
from models import User, UserKey, SensitiveData
from security import hash_password, verify_password
from kms import generate_user_key, encrypt_key, decrypt_key, encrypt_data, decrypt_data
from config import PEPPER
import os

# In a real setup, MASTER_KEY would be securely loaded from env or vault
MASTER_KEY = os.getenv('MASTER_KEY', '32_byte_master_key_32_byte_master_').encode()[:32]

def create_user(db: Session, username: str, password: str):
    salt = os.urandom(16).hex()
    pw_hash = hash_password(password, salt)
    user = User(username=username, password_hash=pw_hash, salt=salt)
    db.add(user)
    db.commit()
    db.refresh(user)
    # KMS: generate and store encrypted user key
    user_key = generate_user_key()
    encrypted = encrypt_key(MASTER_KEY, user_key)
    key_entry = UserKey(user_id=user.id, encrypted_key=encrypted)
    db.add(key_entry)
    db.commit()
    return user

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.salt, user.password_hash):
        return None
    return user

def store_sensitive(db: Session, user_id: int, plaintext: str, description: str = None):
    key_entry = db.query(UserKey).filter(UserKey.user_id == user_id).first()
    user_key = decrypt_key(MASTER_KEY, key_entry.encrypted_key)
    encrypted = encrypt_data(user_key, plaintext.encode())
    data = SensitiveData(user_id=user_id, data=encrypted, description=description)
    db.add(data)
    db.commit()
    db.refresh(data)
    return data

def get_sensitive(db: Session, user_id: int):
    key_entry = db.query(UserKey).filter(UserKey.user_id == user_id).first()
    user_key = decrypt_key(MASTER_KEY, key_entry.encrypted_key)
    entries = db.query(SensitiveData).filter(SensitiveData.user_id == user_id).all()
    result = []
    for e in entries:
        plaintext = decrypt_data(user_key, e.data).decode()
        result.append({'id': e.id, 'description': e.description, 'plaintext': plaintext})
    return result

