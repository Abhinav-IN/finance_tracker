from api.utils.hashing import verify_password, hashing_password
from api.models.account import Account
from api.models.category import Category
from api.models.user import User
from api.models.transaction import Transaction
from api.models.budget import Budget
from api.models.investment import Investment
from api.models.subscription import Subscription
from api.schemas.user import UserProfile, passwordRequest
from api.utils.validator import gender_check
from datetime import date
from fastapi import HTTPException, status
from pydantic import EmailStr
from sqlalchemy import delete, or_
from sqlalchemy.orm import Session


def get_profile_service(user_id: int, db: Session):
    curr_user = db.query(User).filter(User.id == user_id).first()
    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfile.model_validate(curr_user)  

def update_username_service(newUserName : str, user_id : int, db : Session):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    
    curr_user.user_name = newUserName

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating username")
    
    return

def update_fullname_service(newFirstName : str, newLastName : str, user_id : int, db : Session):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    
    curr_user.first_name = newFirstName
    curr_user.last_name = newLastName

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating full name")
    
    return

def update_email_service(newEmail : EmailStr, user_id : int, db : Session):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    
    curr_user.email = newEmail

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating email")
    
    return

def update_dob_service(new_dob : date, user_id : int, db : Session):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    
    curr_user.dob = new_dob

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating date of birth")
    
    return

def update_gender_service(new_gender : str, user_id : int, db : Session):
    final_gender = gender_check(new_gender)
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")

    curr_user.gender = final_gender

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating gender")

    return



def delete_profile_service(user_id: int, db: Session):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.query(Transaction).filter(Transaction.user_id == user_id).delete(synchronize_session=False)
    db.query(Budget).filter(Budget.user_id == user_id).delete(synchronize_session=False)
    db.query(Subscription).filter(Subscription.user_id == user_id).delete(synchronize_session=False)
    db.query(Category).filter(Category.user_id == user_id).delete(synchronize_session=False)  

    db.query(Investment).filter(Investment.user_id == user_id).delete(synchronize_session=False)

    db.query(Account).filter(Account.user_id == user_id).delete(synchronize_session=False)

    curr_user_query.delete(synchronize_session=False)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in deleting profile")


def change_password_service(user_id: int, password_request: passwordRequest, db: Session):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password_request.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    user.hashed_password = hashing_password(password_request.new_password)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in updating password")

    return { "message": "Password updated successfully" }
