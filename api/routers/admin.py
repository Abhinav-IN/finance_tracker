from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.admin import UserRoleUpdate, UserStatusUpdate
from api.services.admin_service import update_user_role_service, update_user_status_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Admin'], prefix='/api/v1/admin')

@router.put("/update-role", status_code=status.HTTP_200_OK)
def update_user_role(
    request: UserRoleUpdate,
    admin: dict = Depends(require_roles("admin")),
    db: Session = Depends(get_db)
):
    return update_user_role_service(request, admin, db)

@router.put("/status/{user_id}", status_code=status.HTTP_200_OK)
def update_user_status(
    user_id: int,
    status_data: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin_data: dict = Depends(require_roles("admin"))
):
    return update_user_status_service(user_id, status_data, db, admin_data)