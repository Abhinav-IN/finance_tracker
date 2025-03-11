from pydantic import BaseModel, EmailStr

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
    
