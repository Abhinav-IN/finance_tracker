import datetime
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class TransactionRequest(BaseModel):
    amount : int 
    description : str
    category_name : str
    transaction_type_name : str
    payment_mode_name : str

    @field_validator("amount")
    def validate_amount(cls, amount):
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")
        return amount

class TransactionResponse(BaseModel):
    amount : int
    description : str
    transaction_id : int
    timestamp : datetime.datetime
    transaction_type_id : int
    transaction_type_name : str
    category_id : int
    category_name : str
    payment_mode_id : int
    payment_mode_name : str

    class Config:
        from_attributes = True

class getTransactionParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    transaction_id : Optional[int] = Field(None, description="ID of a transaction")
    exact_amount : Optional[int] = Field(None, description="Exact amount transaction")
    greater_amount : Optional[int] = Field(None, gt=0, description="Transactions greater than this amount")
    lower_amount : Optional[int] = Field(None, gt=0, description="Transactions smaller than this amount")
    date : Optional[datetime.date] = Field(None, description="Date of transaction")
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit
    