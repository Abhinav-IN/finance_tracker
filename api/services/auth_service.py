from api.core.config import settings
from api.database.session import get_db
from api.models.user import User, UserRole
from api.schemas.user import userRegister, userLogin, refreshRequest, PasswordResetRequest, PasswordResetConfirm
from api.services.token_service import create_verification_token_service, create_access_token_service, verify_token_service, create_password_request_token_service
from api.utils.hashing import hashing_password, verify_password
from api.workers.celery_worker import verification_email, password_reset_email
from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


from api.logger import create_info_logger

auth_logger = create_info_logger("Auth Logger")


def authenticate_user_service(user_credentials : userLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        return False
    return user

def register_user_service(user: userRegister, db: Session = Depends(get_db)):
    hashed_password = hashing_password(user.password)

    new_user = User(
        **user.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
        role=UserRole.user,
        last_password_change_at=datetime.now(timezone.utc),
        last_five_passwords=[hashed_password],
        is_active=False,
        is_suspended=False,
    )

    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or Email already exist")

    verification_token = create_verification_token_service({"user_id": new_user.id})
    token_expiry = datetime.now(timezone.utc) + timedelta(minutes=settings.verification_token_expire_in_minutes)

    new_user.account_verification_token_expires_at = token_expiry
    db.commit()

    verification_link = f"https://finance_tracker.com/verify?token={verification_token}"
    auth_logger.info(f" Verification token: {verification_token}")
    verification_email(new_user.email, verification_link)

    return new_user

def login_service(user_credentials: userLogin, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    lock_window = timedelta(minutes=settings.block_duration)

    db_user = db.query(User).filter(User.email == user_credentials.email).first()

    if db_user and db_user.failed_login_attempts >= settings.maximum_failed_attempts:
        last_failed_time = db_user.last_failed_attempt_at

        if last_failed_time and last_failed_time.tzinfo is None:
            last_failed_time = last_failed_time.replace(tzinfo=timezone.utc)

        if last_failed_time and (now - last_failed_time < lock_window):
            time_left = (last_failed_time + lock_window) - now
            minutes_left = max(1, int(time_left.total_seconds() // 60))
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Too many failed login attempts. Try again in {minutes_left} minutes."
            )
        else:
            db_user.failed_login_attempts = 0
            db_user.last_failed_attempt_at = None
            db.commit()

    user = authenticate_user_service(user_credentials, db)

    if not user:
        if db_user:
            if db_user.last_failed_attempt_at and db_user.last_failed_attempt_at.tzinfo is None:
                db_user.last_failed_attempt_at = db_user.last_failed_attempt_at.replace(tzinfo=timezone.utc)

            if db_user.last_failed_attempt_at and (now - db_user.last_failed_attempt_at < lock_window):
                db_user.failed_login_attempts += 1
            else:
                db_user.failed_login_attempts = 1  
            db_user.last_failed_attempt_at = now
            db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not verified.")
    if user.is_suspended:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended.")

    user.failed_login_attempts = 0
    user.last_failed_attempt_at = None
    user.last_login_at = now
    db.commit()

    access_token = create_access_token_service({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "type": "bearer"
    }

def refresh_access_token_service(token: refreshRequest, db: Session = Depends(get_db)):
    old_access_token = token.access_token

    if not old_access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token is required, Login again")

    payload = verify_token_service(old_access_token, settings.secret_key, algorithm=settings.algorithm)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload in token")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    if user.is_suspended:
        raise HTTPException(status_code=403, detail="Account is suspended")

    new_access_token = create_access_token_service({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": new_access_token,
        "type": "bearer"
    }

def verify_account_service(token: str, db: Session = Depends(get_db)):
    payload = verify_token_service(token, settings.secret_key, settings.algorithm)
    user_id = payload.get("user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    expiry = user.account_verification_token_expires_at

    if not expiry or expiry.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Verification token expired")

    user.account_verification_token_expires_at = None  
    user.is_active = True  
    db.commit()

    return {"message": "Account successfully verified"}

def password_reset_request_service(user_credential: PasswordResetRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_credential.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    password_token = create_password_request_token_service({"user_id": user.id})

    user.password_reset_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.password_token_expire_in_minutes)
    db.commit()

    reset_link = f"https://finance_tracker.com/reset-password?token={password_token}"

    auth_logger.info(f" Password token: {password_token}")

    password_reset_email(user.email, reset_link)

    return {"message": "If this email is registered, a reset link has been sent."}

def password_reset_confirm_service(user_credential: PasswordResetConfirm, db: Session = Depends(get_db)):
    payload = verify_token_service(user_credential.password_token, settings.secret_key, settings.algorithm)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token payload")

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    expires_at = user.password_reset_token_expires_at
    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)

    if not expires_at or expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Password reset token has expired")

    new_hashed = hashing_password(user_credential.new_password)

    if user.last_five_passwords and new_hashed in user.last_five_passwords:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot reuse your previous passwords")

    user.hashed_password = new_hashed
    user.last_password_change_at = datetime.now(timezone.utc)

    if user.last_five_passwords:
        user.last_five_passwords.insert(0, new_hashed)
        user.last_five_passwords = user.last_five_passwords[:5]
    else:
        user.last_five_passwords = [new_hashed]

    user.password_reset_token_expires_at = None

    auth_logger.info(f" stored passwords is {user.last_five_passwords}")
    db.commit()

    return {"message": "Password successfully reset"}