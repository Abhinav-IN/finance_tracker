from api.utils.validator import gender_check, validate_password_strength
from datetime import date
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional

class UserProfile(BaseModel):
    user_name : str
    first_name : str
    last_name : Optional[str] = Field(None)
    email : EmailStr
    dob : date
    gender : str

    model_config = {
        "from_attributes" : True
    }

    @field_validator("gender")
    @classmethod
    def gender_validator(cls, value):
        return gender_check(value)

class passwordRequest(BaseModel):
    old_password : str
    new_password : str

    @field_validator("new_password", mode="after")
    def password_strength(cls, value):
        return validate_password_strength(value)