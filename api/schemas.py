from pydantic import BaseModel

class createProfile(BaseModel):
    user_name : str
    password : str
    email : str

class Profile(BaseModel):
    user_name : str
    email : str
    id : int
    
