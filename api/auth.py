from datetime import datetime, timedelta
from typing import Optional
import os

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

# Secret for demo only; recommend using env var
SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-me-please'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/api/token')

# Dummy in-memory user store for demo
_fake_users = {
    'admin': {'username': 'admin', 'full_name': 'Administrator', 'hashed_password': pwd_context.hash('adminpass'), 'role': 'admin'}
}


def authenticate_user(username: str, password: str):
    u = _fake_users.get(username)
    if not u:
        return None
    if not pwd_context.verify(password, u['hashed_password']):
        return None
    return u


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    encoded = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail='Could not validate credentials')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = _fake_users.get(username)
    if user is None:
        raise credentials_exception
    return user


def login(form_data: OAuth2PasswordRequestForm):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail='Incorrect username or password')
    token = create_access_token({'sub': user['username'], 'role': user.get('role')})
    return {'access_token': token, 'token_type': 'bearer'}
