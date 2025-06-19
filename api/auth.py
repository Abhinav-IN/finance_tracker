from fastapi import APIRouter, status, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from . import schemas, database, utils, models, oauth2, reddis_handler, celery_worker
from api.config import settings

router = APIRouter(tags=['Authentication'], prefix='/user')

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.userOut)
def create_user(user:schemas.userIn, db : Session = Depends(database.get_db)):
    hashed_password = utils.hashing_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post("/login", status_code=status.HTTP_200_OK)
def login(user_credentials : schemas.userLogin, request : Request, db : Session = Depends(database.get_db)):
    ip = utils.get_client_ip(request)
    block_key = f"Blocked : {ip}"

    if reddis_handler.get(block_key):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are currently blocked for multiple failed attempts")

    redis_key = f"Failed_login_attempt : {ip}"
    raw_value = reddis_handler.get(redis_key)
    attempts = int(raw_value) if raw_value else 0

    if attempts >= settings.maximum_failed_attempts:
        reddis_handler.setex(block_key, settings.block_duration, 1)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Too many failed login attempts")

    user = utils.authenticate_user(user_credentials, db)

    if not user:
        reddis_handler.incr(redis_key)
        
        if attempts == 0:
            reddis_handler.setex(redis_key, settings.block_duration, 1)
        
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invlaid credentials")
            

    reddis_handler.delete(redis_key)
    reddis_handler.delete(block_key)

    access_token = oauth2.create_access_token({"user_id" : user.id})
    refresh_token = oauth2.create_refresh_token({"user_id" : user.id})

    reddis_handler.store_refresh_token(user.id, refresh_token, expires_in=10080)

    
    return {"access_token" : access_token,
            "refresh_token" : refresh_token,
            "type" : "bearer"}

@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh(token : schemas.Refresh):
    refresh_token = token.token

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required")
    
    payload = oauth2.verify_token(refresh_token, settings.secret_key, algorithm=settings.algorithm)
    user_id = payload.get("user_id")

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid payload in token")
    
    redis_key = f"refresh_token : {user_id}"
    stored_token = reddis_handler.get(redis_key)

    if stored_token != refresh_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Session expire login again")
    
    reddis_handler.delete(redis_key)

    new_access_token = oauth2.create_access_token({"user_id" : user_id})
    new_refresh_token = oauth2.create_refresh_token({"user_id" : user_id})

    reddis_handler.store_refresh_token(user_id, refresh_token, expires_in=10080)

    return {"access_token" : new_access_token,
            "refresh_token" : new_refresh_token,
            "type" : "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token : schemas.Refresh):
    refresh_token = token.token

    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token is required")
    
    payload = oauth2.verify_token(refresh_token, settings.secret_key, algorithm=settings.algorithm)
    user_id = payload.get("user_id")

    
    redis_key = f"refresh_token : {user_id}"
    reddis_handler.delete(redis_key)

    return {"message" : "Logout successfull"}

@router.post("/password-reset-request", status_code=status.HTTP_202_ACCEPTED)
def password_reset_request(user_credential : schemas.PasswordResetRequest, db : Session = Depends(database.get_db)):
    user = db.query(models.User).filter(user_credential.email == models.User.email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    password_token = oauth2.create_password_request_token({"user_id" : user.id})
   
    reset_link = f"https://finance_tracker.com/reset-password?token={password_token}"

    print(f"password token is : {password_token}")

    celery_worker.send_password_reset_email(user_credential.email, reset_link)

    return {"message": "If this email is registered, a reset link has been sent."}

@router.post("/password-reset-confirm", status_code=status.HTTP_200_OK)
def password_reset_confirm(user_credential : schemas.PasswordResetConfirm, db : Session = Depends(database.get_db)):
    payload = oauth2.verify_token(user_credential.token, settings.secret_key, settings.algorithm)
    user_id = payload.get("user_id")
    user = db.query(models.User).filter(user_id == models.User.id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    new_hashed_password = utils.hashing_password(user_credential.new_password)
    user.password = new_hashed_password
    db.commit()
    return {"message": "Password successfully reset"}    