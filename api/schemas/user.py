from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserProfile(BaseModel):
    username : str
    first_name : str
    last_name : Optional[str] = Field(None)
    email : EmailStr
    dob : datetime.date
    gender : str 
