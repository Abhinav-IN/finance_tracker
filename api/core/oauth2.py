from api.core.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def get_current_user(token: str = Depends(oauth2_scheme)):
    from api.services.token_service import verify_token_service
    payload = verify_token_service(token, settings.secret_key, settings.algorithm)
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
