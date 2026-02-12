from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.user import UserProfile, passwordRequest
from api.services.user_service import get_profile_service, update_username_service, update_fullname_service, update_email_service, update_dob_service, update_gender_service,  delete_profile_service, change_password_service
from datetime import date
from api.utils.enums import UserRole
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['User'], prefix='/api/v1/user')

@router.get("/profile", status_code=status.HTTP_200_OK, response_model=UserProfile)
def get_profile(user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return get_profile_service(user["id"], db)

@router.put("/update_username", status_code=status.HTTP_200_OK)
def update_username(newUserName : str, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_username_service(newUserName, user["id"], db)

@router.put("/update_fullname", status_code=status.HTTP_200_OK)
def update_fullname(newFirstName : str, newLastName : str, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_fullname_service(newFirstName, newLastName, user["id"], db)

@router.put("/update_email", status_code=status.HTTP_200_OK)
def update_email(newEmail : str, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_email_service(newEmail, user["id"], db)

@router.put("/update_dob", status_code=status.HTTP_200_OK)
def update_dob(new_dob : date, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_dob_service(new_dob, user["id"], db)

@router.put("/update_gender", status_code=status.HTTP_200_OK)
def update_gender(new_gender : str, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_gender_service(new_gender, user["id"], db)    

@router.delete("/delete", status_code=status.HTTP_200_OK)
def delete_profile(user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return delete_profile_service(user["id"], db)

@router.put("/change-password", status_code=status.HTTP_200_OK)
def change_password(password_request : passwordRequest, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return change_password_service(user["id"], password_request, db)