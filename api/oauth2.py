from jose import JWTError, jwt, ExpiredSignatureError
from datetime import datetime, timedelta
from .config import settings
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data : dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.access_token_expire_in_minutes)
    to_encode.update({"exp" : expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def verify_token(token : str, secret_key : str, algorithm : str):
    try:
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        return payload
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is tampered")
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired refresh it")

def create_password_request_token(data : dict):
    to_encode = data.copy()
    expiration_time = datetime.now() + timedelta(minutes=settings.password_token_expire_in_minutes)
    to_encode.update({"exp" : expiration_time})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token, settings.secret_key, settings.algorithm)
    user_id: int = payload.get("user_id")
    role: str = payload.get("role")

    if not user_id or not role:
        raise HTTPException(status_code=401, detail="Invalid authentication token")

    return {"id": user_id, "role": role}

def require_roles(*allowed_roles):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have access to perform this action"
            )
        return user
    return role_checker