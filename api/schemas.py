from pydantic import BaseModel, EmailStr, Field, field_validator
import re
from api.utils import validate_password_strength

class userRegister(BaseModel):
    username : str
    email : EmailStr
    password : str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value):
        return validate_password_strength(value)

class userRegisterResponse(BaseModel):
    username: str
    email: str

    class Config:
        from_attributes = True

class userLogin(BaseModel):
    email: EmailStr
    password: str

class userLoginResponse(BaseModel):
    access_token : str
    refresh_token : str
    type : str = Field(default="bearer")

class refreshRequest(BaseModel):
    refresh_token : str

class refreshResponse(userLoginResponse):
    pass

class PasswordResetRequest(BaseModel):
    email : EmailStr

class PasswordResetConfirm(BaseModel):
    password_token: str
    new_password: str = Field(..., min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, value):
        return validate_password_strength(value)

# Schemas related to category
class categoryCreate(BaseModel):
    category_name : str

class categoryResponse(BaseModel):
    category_id : int
    category_name : str
