from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, database, utils, models, oauth2, celery_worker
from api.config import settings
from datetime import datetime

router = APIRouter(tags=['Authentication'], prefix='/user')

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.userRegisterResponse)
def create_user(user:schemas.userRegister, db : Session = Depends(database.get_db)):
    hashed_password = utils.hashing_password(user.password)

    new_user = models.User(
    **user.model_dump(exclude={"password"}),
    hashed_password=hashed_password,    
    role=models.UserRole.user,
    last_password_change_at=datetime.now(),
    last_five_passwords=[hashed_password],
    is_active=True,
    is_suspended=False
)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", status_code=status.HTTP_200_OK, response_model=schemas.userLoginResponse)
def login(user_credentials: schemas.userLogin, db: Session = Depends(database.get_db)):
    user = utils.authenticate_user(user_credentials, db)

    if not user:
        db_user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
        if db_user:
            db_user.login_attempts += 1
            db.commit()

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated.")
    if user.is_suspended:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is suspended.")

    user.login_attempts = 0
    user.last_login_at = datetime.now()
    db.commit()

    access_token = oauth2.create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": access_token,
        "type": "bearer"
    }
@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=schemas.refreshResponse)
def refresh(token: schemas.refreshRequest, db: Session = Depends(database.get_db)):
    old_access_token = token.access_token

    if not old_access_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Access token is required, Login again")

    payload = oauth2.verify_token(old_access_token, settings.secret_key, algorithm=settings.algorithm)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload in token")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    if user.is_suspended:
        raise HTTPException(status_code=403, detail="Account is suspended")

    new_access_token = oauth2.create_access_token({
        "user_id": user.id,
        "role": user.role
    })

    return {
        "access_token": new_access_token,
        "type": "bearer"
    }

from datetime import datetime, timedelta

@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
def password_reset_request(user_credential: schemas.PasswordResetRequest, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == user_credential.email).first()

    if user:
        password_token = oauth2.create_password_request_token({"user_id": user.id})

        user.password_reset_token_expires_at = datetime.now() + timedelta(minutes=settings.password_token_expire_in_minutes)
        db.commit()

        reset_link = f"https://finance_tracker.com/reset-password?token={password_token}"

        print(f"[DEBUG] Password token: {password_token}")

        celery_worker.send_password_reset_email(user.email, reset_link)

    return {"message": "If this email is registered, a reset link has been sent."}

@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
def password_reset_confirm(user_credential: schemas.PasswordResetConfirm, db: Session = Depends(database.get_db)):
    payload = oauth2.verify_token(user_credential.password_token, settings.secret_key, settings.algorithm)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token payload")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.password_reset_token_expires_at or user.password_reset_token_expires_at < datetime.now():
        raise HTTPException(status_code=403, detail="Reset token has expired")

    new_hashed = utils.hashing_password(user_credential.new_password)

    if user.last_five_passwords and new_hashed in user.last_five_passwords:
        raise HTTPException(status_code=400, detail="You cannot reuse your previous passwords.")

    user.hashed_password = new_hashed
    user.last_password_change_at = datetime.utcnow()

    if user.last_five_passwords:
        user.last_five_passwords.insert(0, new_hashed)
        user.last_five_passwords = user.last_five_passwords[:5]
    else:
        user.last_five_passwords = [new_hashed]

    user.password_reset_token_expires_at = None

    db.commit()

    return {"message": "Password successfully reset"}

@router.put("/update-role", status_code=200)
def update_user_role(
    request: schemas.UserRoleUpdate,
    admin: dict = Depends(oauth2.require_roles("admin")),
    db: Session = Depends(database.get_db)
):
    target_user = db.query(models.User).filter(models.User.id == request.user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == admin["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    target_user.role = request.role
    db.commit()
    return {"message": f"Role updated to {request.role} for user ID {request.user_id}"}


@router.put("/status/{user_id}", status_code=200)
def update_user_status(
    user_id: int,
    status_data: schemas.UserStatusUpdate,
    db: Session = Depends(database.get_db),
    admin_data: dict = Depends(oauth2.require_roles("admin"))
):
    if user_id == admin_data["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own account status")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = status_data.is_active
    user.is_suspended = status_data.is_suspended
    db.commit()

    return {
        "message": f"User status updated. Active: {user.is_active}, Suspended: {user.is_suspended}"
    }