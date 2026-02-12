from api.utils.enums import TransactionDirection
from pydantic import BaseModel, Field
from typing import Optional, List
from api.schemas.transaction import TransactionResponse

class accountRequest(BaseModel):
    name : str = Field(max_length=104, description="User defined account name eg: Naruto personal acount")
    type : str = Field(max_length=104, description="Account type eg: savings, debit, credit etc")
    bank_name : Optional[str] = Field(default=None, max_length=104)
    balance_amount : Optional[int] = Field(default=0.0, ge=0)
    is_active : bool

class accountResponse(accountRequest):
    id : int

    model_config = {
        "from_attributes" : True
    }   

class AccountQueryParam(BaseModel):
    direction : TransactionDirection
    page : int = Field(1, ge=1, description="Page number starting from 1")
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit
    
class PaginatedTransactionResponse(BaseModel):
    total_pages : int
    current_page : int
    total_transactions : int
    transactions : List[TransactionResponse]
    model_config = {
        "from_attributes" : True
    }
