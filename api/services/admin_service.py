from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.user import User
from api.schemas.admin import UserRoleUpdate, UserStatusUpdate
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session


def update_user_role_service(
    request: UserRoleUpdate,
    admin: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    target_user = db.query(User).filter(User.id == request.user_id).first()

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if target_user.id == admin["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own role")

    target_user.role = request.role
    db.commit()
    return {"message": f"Role updated to {request.role} for user ID {request.user_id}"}

def update_user_status_service(
    user_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_roles("admin"))
):
    if user_id == admin_data["id"]:
        raise HTTPException(status_code=400, detail="You cannot change your own account status")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = status_data.is_active
    user.is_suspended = status_data.is_suspended
    db.commit()

    return {
        "message": f"User status updated. Active: {user.is_active}, Suspended: {user.is_suspended}"
    }