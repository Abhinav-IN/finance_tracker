from api.utils.hashing import verify_password, hashing_password
from api.database.session import get_db
from api.models.category import Category
from api.models.user import User
from api.models.transaction import Transaction
from api.models.budget import Budget
from api.models.investment_goal_link import investment_goal_link
from api.models.investment import Investment
from api.models.investment_goal import InvestmentGoal
from api.models.subscription import Subscription
from api.schemas.user import UserProfile, passwordRequest
from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, or_
from sqlalchemy.orm import Session


def get_profile_service(user_id: int, db: Session = Depends(get_db)):
    curr_user = db.query(User).filter(User.id == user_id).first()
    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserProfile.model_validate(curr_user)  

def update_profile_service(userProfileRequest: UserProfile, user_id: int, db: Session = Depends(get_db)):
    curr_user_query = db.query(User).filter(User.id == user_id)     
    curr_user = curr_user_query.first()
    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    curr_user_query.update({
        "username": userProfileRequest.username,
        "first_name": userProfileRequest.first_name,
        "last_name": userProfileRequest.last_name,
        "email": userProfileRequest.email,
        "dob": userProfileRequest.dob,
        "gender": userProfileRequest.gender
    }, synchronize_session=False)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating user profile")

    return UserProfile.model_validate(curr_user)


def delete_profile_service(user_id: int, db: Session = Depends(get_db)):
    curr_user_query = db.query(User).filter(User.id == user_id)
    curr_user = curr_user_query.first()

    if not curr_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    db.query(Transaction).filter(Transaction.user_id == user_id).delete(synchronize_session=False)
    db.query(Budget).filter(Budget.user_id == user_id).delete(synchronize_session=False)
    db.query(Subscription).filter(Subscription.user_id == user_id).delete(synchronize_session=False)
    db.query(Category).filter(Category.user_id == user_id).delete(synchronize_session=False)  

    investment_ids = [inv_id for (inv_id,) in db.query(Investment.investment_id).filter(Investment.user_id == user_id).all()]
    goal_ids = [goal_id for (goal_id,) in db.query(InvestmentGoal.goal_id).filter(InvestmentGoal.user_id == user_id).all()]

    if investment_ids or goal_ids:
        stmt = delete(investment_goal_link).where(
            or_(
                investment_goal_link.c.investment_id.in_(investment_ids),
                investment_goal_link.c.goal_id.in_(goal_ids)
            )
        )
        db.execute(stmt)

    db.query(InvestmentGoal).filter(InvestmentGoal.user_id == user_id).delete(synchronize_session=False)
    db.query(Investment).filter(Investment.user_id == user_id).delete(synchronize_session=False)

    curr_user_query.delete(synchronize_session=False)

    db.commit()

def change_password_service(user_id: int, password_request: passwordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not verify_password(password_request.old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect")

    user.hashed_password = hashing_password(password_request.new_password)
    db.commit()

    return { "message": "Password updated successfully" }
