from api.models.user import User
from api.schemas.admin import UserRoleUpdate, UserStatusUpdate
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def update_user_role_service(request: UserRoleUpdate, admin: dict,db: Session):
    target_user = db.query(User).filter(User.id == request.user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == admin["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    target_user.role = request.role
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in updating role")
    return {"message": f"Role updated to {request.role} for user ID {request.user_id}"}

def update_user_status_service(user_id: int, status_data: UserStatusUpdate, db: Session, admin_data: dict):
    if user_id == admin_data["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own account status")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = status_data.is_active
    user.is_suspended = status_data.is_suspended

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Somethinf went wrong in updating status")

    return {
        "message": f"User status updated. Active: {user.is_active}, Suspended: {user.is_suspended}"
    }