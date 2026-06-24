from api.utils.validator import gender_check, validate_password_strength
import datetime
from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional

class userRegister(BaseModel):
    user_name : str
    first_name : str
    last_name : Optional[str] = None
    email : EmailStr
    dob : datetime.date
    gender : str
    password : str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def password_strength(cls, value):
        return validate_password_strength(value)
    
    @field_validator("gender")
    @classmethod
    def gender_validator(cls, value):
        return gender_check(value)

class userRegisterResponse(BaseModel):
    user_name: str
    email: str

    class Config:
        from_attributes = True

class userLogin(BaseModel):
    email: EmailStr
    password: str

class userLoginResponse(BaseModel):
    access_token : str
    type : str = Field(default="bearer")

class refreshRequest(BaseModel):
    access_token : str

class refreshResponse(userLoginResponse):
    pass
