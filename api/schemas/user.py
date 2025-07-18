from api.utils.validator import gender_check
from datetime import datetime
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional

class UserProfile(BaseModel):
    username : str
    first_name : str
    last_name : Optional[str] = Field(None)
    email : EmailStr
    dob : datetime.date
    gender : str

    @field_validator("gender")
    @classmethod
    def gender_validator(cls, value):
        return gender_check(value)

