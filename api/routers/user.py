from api.core.oauth2 import get_current_user
from api.database.session import get_db
from api.schemas.user import UserProfile, passwordRequest
from api.services.user_service import get_profile_service, update_profile_service, delete_profile_service, change_password_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['User'], prefix='/api/v1/user')

@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserProfile)
def get_profile(user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    return get_profile_service(user["id"], db)

@router.put("/update-profile", status_code=status.HTTP_200_OK, response_model=UserProfile)
def update_profile(userProfileRequest : UserProfile, user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    return update_profile_service(userProfileRequest, user["id"], db)

@router.delete("/delete-profile", status_code=status.HTTP_200_OK)
def delete_profile(user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    return delete_profile_service(user["id"], db)

@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(password_request : passwordRequest, user : dict = Depends(get_current_user), db : Session = Depends(get_db)):
    return change_password_service(user["id"], password_request, db)