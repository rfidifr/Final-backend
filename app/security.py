import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv
import secrets


load_dotenv()

# Configuration from .env
SECRET_KEY = 's' #os.getenv("SECRET_KEY")
ALGORITHM = 'HS256' #os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 600 #int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_secretkey():
    return secrets.token_hex(32)

