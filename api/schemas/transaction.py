from api.utils.validator import validate_amount
import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal, List
from zoneinfo import ZoneInfo

def get_current_time_india():
    return datetime.datetime.now(ZoneInfo("Asia/Kolkata"))

class ExpenseRequest(BaseModel):
    expense_name : str = Field(max_length=64)
    expense_date: datetime.datetime = Field(default_factory=get_current_time_india)
    price : float = Field(gt=0)
    expense_type_name : str = Field(default="Nill")
    category_name : str
    payment_mode_name : str
    account_name : Optional[str] = Field(default=None, description="Account name")
    additional_note : str = Field(max_length=140)

    @model_validator(mode="after")
    def validate_expense(self):
        validate_amount(self)
        return self

class ExpenseResponse(ExpenseRequest):
    expense_id : int
    expense_type_id : int
    category_id : int
    payment_mode_id : int
    account_id : Optional[int] = None

    class Config:
        from_attributes = True

class PaginatedExpenseResponse(BaseModel):
    total_pages: int
    current_page: int
    total_expenses: int
    expenses: List[ExpenseResponse]

    model_config = {
        "from_attributes" : True
    }

class ExpenseOverview(BaseModel):
    total_expense_last_30_days : float
    total_expense_last_7_days : float
    total_expense_current_month: float
    average_monthly_expense : float
    average_weekly_expense : float

class BudgetFeedback(BaseModel):
    status: Literal["under", "over"]
    budget_amount: float
    spent: float
    remaining: float
    message: str
    
class IncomeRequest(BaseModel):
    income_name : str = Field(max_length=64)
    recieved_date: datetime.datetime = Field(default_factory=get_current_time_india)
    amount : float
    income_type_name : str = Field(default="Nill")
    category_name : str
    payment_mode_name : str
    account_name : Optional[str] = Field(default=None, description="Account name")
    additional_note : str = Field(max_length=140)

    @model_validator(mode="after")
    def validate_income(self):
        validate_amount(self)
        return self

class IncomeResponse(IncomeRequest):
    income_id : int
    income_type_id : int
    category_id : int
    payment_mode_id : int
    account_id : Optional[int] = None

    model_config = {
        "from_attributes" : True
    }

class PaginatedIncomeResponse(BaseModel):
    total_pages: int
    current_page: int
    total_incomes: int
    incomes: List[IncomeResponse]

    model_config = {
        "from_attributes" : True
    }

class IncomeOverview(BaseModel):
    total_income_last_30_days : float
    total_income_last_7_days : float
    total_income_current_month: float
    average_monthly_income : float
    average_weekly_income : float

class TransactionQueryParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    transaction_id : Optional[int] = Field(None, description="Income ID or Expense ID")
    exact_amount : Optional[int] = Field(None, description="Exact amount transaction")
    greater_amount : Optional[int] = Field(None, gt=0, description="Transactions greater than this amount")
    lower_amount : Optional[int] = Field(None, gt=0, description="Transactions smaller than this amount")
    date : Optional[datetime.date] = Field(None, description="Date of transaction")
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit