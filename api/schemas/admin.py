from api.utils.enums import UserRole
from pydantic import BaseModel

class UserRoleUpdate(BaseModel):
    role: UserRole
    user_id : int

class UserStatusUpdate(BaseModel):
    is_active: bool
    is_suspended: bool