import os
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv

from auth.verify_token import JWT_SECRET  
load_dotenv() 
SECRET_KEY = os.getenv("JWT_SECRET", "supersecret")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120
JWT_SECRET = os.getenv("JWT_SECRET")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token:str):
    return jwt.decode(token,algorithms=ALGORITHM,key=JWT_SECRET) 