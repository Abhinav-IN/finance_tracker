from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from api.utils.enums import TransactionDirection
from api.utils.time import ist_now

class TransactionBase(BaseModel):
    title : str = Field(max_length=64)
    date : datetime = Field(default_factory=ist_now)
    amount : Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    direction : TransactionDirection
    transaction_type_name : str = Field(default="Nill")
    category_name : str
    payment_mode_name : str
    account_name : Optional[str] = None
    description : Optional[str] = Field(default= None, max_length=140)

class TransactionCreate(TransactionBase):
    pass

class TransactionResponse(BaseModel):
    title : str = Field(max_length=64)
    date : datetime
    amount : Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    direction : TransactionDirection
    description : Optional[str] = Field(default= None, max_length=140)
    id : int
    category_id : int
    payment_mode_id : int
    account_id : Optional[int] = None

    model_config = {"from_attributes" : True}

class PaginatedTransactionResponse(BaseModel):
    total_pages: int
    current_page: int
    total_transactions: int
    transactions: List[TransactionResponse]

    model_config = {"from_attributes" : True}

class ExpenseOverview(BaseModel):
    total_expense_last_30_days : float
    total_expense_last_7_days : float
    total_expense_current_month: float
    average_monthly_expense : float
    average_weekly_expense : float

class IncomeOverview(BaseModel):
    total_income_last_30_days : float
    total_income_last_7_days : float
    total_income_current_month: float
    average_monthly_income : float
    average_weekly_income : float

class BudgetFeedback(BaseModel):
    status: Literal["under", "over"]
    budget_amount: float
    spent: float
    remaining: float
    message: str

class TransactionQueryParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    direction : Optional[TransactionDirection]
    id : Optional[int] = Field(None, description="Income ID or Expense ID")
    exact_amount : Optional[Decimal] = Field(None, description="Exact amount transaction")
    greater_amount : Optional[Decimal] = Field(None, gt=0, description="Transactions greater than this amount")
    lower_amount : Optional[Decimal] = Field(None, gt=0, description="Transactions smaller than this amount")
    date : Optional[datetime] = Field(None, description="Date of transaction") #CHanged From datetime.date to datetime
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit