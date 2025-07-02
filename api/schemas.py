from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from typing import Optional
from .validator import validate_password_strength
import datetime
from enum import Enum

class UserRole(str, Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"
    support = "support"

class userRegister(BaseModel):
    username : str
    first_name : str
    last_name : str
    email : EmailStr
    dob : datetime.date
    gender : str
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
    type : str = Field(default="bearer")

class refreshRequest(BaseModel):
    access_token : str

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
    
class UserRoleUpdate(BaseModel):
    role: UserRole
    user_id : int

class UserStatusUpdate(BaseModel):
    is_active: bool
    is_suspended: bool



# Schemas related to category
class categoryCreate(BaseModel):
    category_name : str

class categoryResponse(BaseModel):
    category_id : int
    category_name : str

#Schemas related to transaction
class TransactionRequest(BaseModel):
    amount : int 
    description : str
    category_name : str
    transaction_type_name : str

class TransactionResponse(BaseModel):
    amount : int
    description : str
    timestamp : datetime.datetime
    transaction_type_id : int
    transaction_type_name : str
    category_id : int
    category_name : str

    class Config:
        from_attributes = True

class getTransactionParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    transaction_id : Optional[int] = Field(None, description="ID of a transaction")
    exact_amount : Optional[int] = Field(None, description="Exact amount transaction")
    greater_amount : Optional[int] = Field(None, gt=0, description="Transactions greater than this amount")
    lower_amount : Optional[int] = Field(None, gt=0, description="Transactions smaller than this amount")
    date : Optional[datetime.date] = Field(None, description="Date of transaction")
    category_id : Optional[int] = Field(None, description="ID of category")
    transaction_type_id : Optional[int] = Field(None, description="IDof transaction type")
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit
    