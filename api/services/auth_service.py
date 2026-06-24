from api.core.config import settings
from api.database.session import get_db
from api.models.user import User, UserRole
from api.schemas.auth import userRegister, userLogin, refreshRequest
from api.services.token_service import create_access_token_service, verify_token_service
from api.utils.hashing import hashing_password, verify_password
from api.utils.time import ist_now, IST
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
from api.utils.logger import create_info_logger

auth_logger = create_info_logger("Auth Logger")

def authenticate_user_service(user_credentials : userLogin, db: Session):
    user = db.query(User).filter(User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        return False
    return user

def register_user_service(user: userRegister, db: Session):
    hashed_password = hashing_password(user.password)

    new_user = User(
        **user.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
        role=UserRole.USER,
        is_active=True,
        is_suspended=False,
    )

    db.add(new_user)
    try:
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or Email already exist")

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Somethign went wrong in verification token setup")

    return new_user

def login_service(user_credentials: userLogin, db: Session):
    lock_window = timedelta(minutes=settings.block_duration)

    db_user = db.query(User).filter(User.email == user_credentials.email).first()

    if db_user and db_user.failed_login_attempts >= settings.maximum_failed_attempts:
        last_failed_time = db_user.last_failed_attempt_at

        if last_failed_time and last_failed_time.tzinfo is None:
            last_failed_time = last_failed_time.replace(tzinfo=IST)

        if last_failed_time and (ist_now() - last_failed_time < lock_window):
            time_left = (last_failed_time + lock_window) - ist_now()
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
                db_user.last_failed_attempt_at = db_user.last_failed_attempt_at.replace(tzinfo=IST)

            if db_user.last_failed_attempt_at and (ist_now() - db_user.last_failed_attempt_at < lock_window):
                db_user.failed_login_attempts += 1
            else:
                db_user.failed_login_attempts = 1  
            db_user.last_failed_attempt_at = ist_now()
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
    user.last_login_at = ist_now()
    db.commit()

    access_token = create_access_token_service({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "type": "bearer"
    }

def refresh_access_token_service(token: refreshRequest, db: Session):
    old_access_token = token.access_token

    if not old_access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token is required, Login again")

    payload = verify_token_service(old_access_token, settings.secret_key, algorithm=settings.algorithm, ignore_exp=True)
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

def demo_login_service(db: Session):
    user = db.query(User).filter(User.email == settings.demo_email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Demo account ({settings.demo_email}) not found.",
        )

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo account is not active.")
    if user.is_suspended:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Demo account is suspended.")

    user.failed_login_attempts = 0
    user.last_failed_attempt_at = None
    user.last_login_at = ist_now()
    db.commit()

    access_token = create_access_token_service({
        "user_id": user.id,
        "role": user.role,
    })

    return {
        "access_token": access_token,
        "type": "bearer",
    }
