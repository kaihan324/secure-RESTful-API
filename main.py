from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from schemas import UserCreate, Token, SensitiveDataIn, SensitiveDataOut
from crud import create_user, authenticate_user, store_sensitive, get_sensitive
from security import create_access_token, decode_access_token
from models import User
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from fastapi import UploadFile, File
from kms import (
    MASTER_KEY, generate_user_key, encrypt_key,
    save_encrypted_key, load_encrypted_key
)



Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')


login_attempts = {}  # key = username, value = {'count': int, 'last_attempt': datetime}
LOCKOUT_TIME = timedelta(minutes=5)
MAX_ATTEMPTS = 5

@app.post('/register', response_model=Token)
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == user.username).first()
    if existing:
        raise HTTPException(status_code=400, detail='Username already exists')
    new_user = create_user(db, user.username, user.password)
    access_token = create_access_token({'sub': new_user.username})
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/token', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    username = form_data.username
    now = datetime.utcnow()


    attempt = login_attempts.get(username)
    if attempt:
        if attempt['count'] >= MAX_ATTEMPTS and now - attempt['last_attempt'] < LOCKOUT_TIME:
            raise HTTPException(
                status_code=429,
                detail='Too many login attempts. Try again later.'
            )
        elif now - attempt['last_attempt'] >= LOCKOUT_TIME:
 
            login_attempts[username] = {'count': 0, 'last_attempt': now}

    user = authenticate_user(db, username, form_data.password)
    if not user:
        if username not in login_attempts:
            login_attempts[username] = {'count': 1, 'last_attempt': now}
        else:
            login_attempts[username]['count'] += 1
            login_attempts[username]['last_attempt'] = now
        raise HTTPException(status_code=401, detail='Invalid credentials')

  
    if username in login_attempts:
        del login_attempts[username]

    access_token = create_access_token({'sub': user.username})
    return {'access_token': access_token, 'token_type': 'bearer'}

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_access_token(token)
        username: str = payload.get('sub')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail='Invalid user')
    return user

@app.post('/data', response_model=SensitiveDataOut)
def add_data(data_in: SensitiveDataIn, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entry = store_sensitive(db, current_user.id, data_in.plaintext, data_in.description)
    return {'description': entry.description, 'plaintext': data_in.plaintext}

@app.get('/data', response_model=list[SensitiveDataOut])
def read_data(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return get_sensitive(db, current_user.id)

@app.post("/kms")
def generate_kms_key(current_user: User = Depends(get_current_user)):
    user_key = generate_user_key()
    encrypted = encrypt_key(MASTER_KEY, user_key)
    save_encrypted_key(current_user.id, encrypted)
    return {"message": "Key generated and stored securely."}

@app.get("/kms")
def get_kms_key(current_user: User = Depends(get_current_user)):
    try:
        encrypted = load_encrypted_key(current_user.id)
        return {
            "user_id": current_user.id,
            "encrypted_key_hex": encrypted.hex()
        }
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Key not found for this user.")