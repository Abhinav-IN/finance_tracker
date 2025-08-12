from pydantic import BaseModel, Field
from typing import Optional, List
from api.schemas.transaction import IncomeResponse, ExpenseResponse

class accountRequest(BaseModel):
    account_name : str = Field(max_length=104, description="User defined account name eg: Naruto personal acount")
    account_type : str = Field(max_length=104, description="Account type eg: savings, debit, credit etc")
    bank_name : Optional[str] = Field(default=None, max_length=104)
    balance_amount : Optional[int] = Field(default=0.0, ge=0)
    is_active : bool

class accountResponse(accountRequest):
    account_id : int

    model_config = {
        "from_attributes" : True
    }   

class AccountQueryParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit

class PaginatedIncomeResponse(BaseModel):
    total_pages: int
    current_page: int
    total_incomes: int
    incomes: List[IncomeResponse]

    model_config = {
        "from_attributes" : True
    }

class PaginatedExpenseResponse(BaseModel):
    total_pages: int
    current_page: int
    total_expenses: int
    expenses: List[ExpenseResponse]

    model_config = {
        "from_attributes" : True
    }

