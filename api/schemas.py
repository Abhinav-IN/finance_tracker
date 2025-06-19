from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from api.utils import validate_password_strength

class userIn(BaseModel):
    username : str
    email : EmailStr
    password : str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value):
        return validate_password_strength(value)

class userOut(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True

class userLogin(BaseModel):
    username: str
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email : EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, value):
        return validate_password_strength(value)
    
class Refresh(BaseModel):
    token : str