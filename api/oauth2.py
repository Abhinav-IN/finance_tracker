from jose import JWTError, jwt
from datetime import datetime, timedelta
from api.config import settings
from fastapi import HTTPException, status

def create_access_token(data : dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.access_token_expire_in_minutes)
    to_encode.update({"exp" : expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data : dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.refresh_token_expire_in_minutes)
    to_encode.update({"exp" : expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token : str, secret_key : str, algorithm : str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is tampered")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")

def create_password_request_token(data : dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.password_token_expire_in_minutes)
    to_encode.update({"exp" : expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt