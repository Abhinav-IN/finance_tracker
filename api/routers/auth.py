from api.database.session import get_db
from api.schemas.auth import PasswordResetRequest, PasswordResetConfirm, refreshRequest, refreshResponse, userLogin, userLoginResponse, userRegister, userRegisterResponse
from api.services.auth_service import login_service, password_reset_request_service, password_reset_confirm_service, refresh_access_token_service, register_user_service, verify_account_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Authentication'], prefix='/api/v1/auth')


@router.options("/register")
@router.options("/login")
@router.options("/refresh")
@router.options("/password-reset-request")
@router.options("/password-reset-confirm")
def auth_options():
    """Allow CORS preflight for auth routes."""
    return None


@router.post("/login", status_code=status.HTTP_200_OK, response_model=userLoginResponse)
def login(user_credentials: userLogin, db: Session = Depends(get_db)):
   return login_service(user_credentials, db)
    
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=userRegisterResponse)
def register_user(user: userRegister, db: Session = Depends(get_db)):
    return register_user_service(user, db)

@router.get("/verify-account")
def verify_account(token: str, db: Session = Depends(get_db)):
    return verify_account_service(token, db)
    
@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=refreshResponse)
def refresh(token: refreshRequest, db: Session = Depends(get_db)):
    return refresh_access_token_service(token, db)

@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
def password_reset_request(user_credential: PasswordResetRequest, db: Session = Depends(get_db)):
    return password_reset_request_service(user_credential, db)
    
@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
def password_reset_confirm(user_credential: PasswordResetConfirm, db: Session = Depends(get_db)):
    return password_reset_confirm_service(user_credential, db)