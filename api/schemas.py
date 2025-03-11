from pydantic import BaseModel, EmailStr
from typing import Optional

class createProfile(BaseModel):
    user_name : str
    password : str
    email : EmailStr

    class Config:
        from_attributes = True

class Profile(BaseModel):
    user_name : str
    email : str
    id : int

    class Config:
        from_attributes = True
    
class userLogin(BaseModel):
    email : EmailStr
    password : str

class token(BaseModel):
    access_token : str
    token_type : str

class token_data(BaseModel):
    id : Optional[str] = None

class ProfileWithToken(BaseModel):
    profile: Profile 
    token: token

    class Config:
        from_attributes = True