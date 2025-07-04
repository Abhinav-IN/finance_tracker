from api.core.config import settings
from datetime import datetime, timedelta  
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, jwt, JWTError

def create_access_token_service(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.access_token_expire_in_minutes)  
    to_encode.update({"exp": expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token_service(token: str, secret_key: str, algorithm: str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is tampered")

def create_password_request_token_service(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.password_token_expire_in_minutes)  
    to_encode.update({"exp": expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_verification_token_service(data: dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.verification_token_expire_in_minutes)  
    to_encode.update({"exp": expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt
