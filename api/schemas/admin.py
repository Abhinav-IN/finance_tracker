from enum import Enum
from pydantic import BaseModel

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"
    support = "support"

class UserRoleUpdate(BaseModel):
    role: UserRole
    user_id : int

class UserStatusUpdate(BaseModel):
    is_active: bool
    is_suspended: bool