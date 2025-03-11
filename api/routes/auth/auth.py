from fastapi import APIRouter, Depends, HTTPException, status
from api import schemas, models, utils, Oauth2
from sqlalchemy.orm import Session
from api.database import get_db
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login")
def user_login(user_credential : OAuth2PasswordRequestForm = Depends(), db : Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == user_credential.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Credenntials are wrong")
    
    if not utils.verify_password(user_credential.password, user.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Credenntials are wrong")

    access_token = Oauth2.create_access_token({"user_id" : user.id})
    return {"Acess Token" : access_token, "token_type" : "bearer"}

