from api.database.session import get_db
from api.models.user import User
from api.schemas.user import UserProfile
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

def get_profile(user_id : int, db : Session = Depends(get_db)):
    curr_user = db.query(User).filter(User.id == user_id).first()
    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserProfile(
        username=curr_user.username,
        first_name=curr_user.first_name,
        last_name=curr_user.last_name,
        email=curr_user.email,
        dob=curr_user.dob,
        gender=curr_user.gender
    )

def update_profile(userProfileRequest : UserProfile, user_id : int, db : Session = Depends(get_db)):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()
    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    curr_user_query.update({
        "username" : userProfileRequest.username,
        "first_name" : userProfileRequest.first_name,
        "last_name" : userProfileRequest.last_name,
        "email" : userProfileRequest.email,
        "dob" : userProfileRequest.dob,
        "gender" : userProfileRequest.gender
    }, synchronize_session=False)

    try:
        db.commit(curr_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating user profile")
    
    return UserProfile(
        username=curr_user.username,
        first_name=curr_user.first_name,
        last_name=curr_user.last_name,
        email=curr_user.email,
        dob=curr_user.dob,
        gender=curr_user.gender
    )