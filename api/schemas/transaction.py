from api.utils.validator import validate_amount, validate_transaction_type
import datetime
from pydantic import BaseModel, Field, model_validator
from typing import Optional, Literal
from zoneinfo import ZoneInfo

def get_current_time_india():
    return datetime.datetime.now(ZoneInfo("Asia/Kolkata"))

class ExpenseRequest(BaseModel):
    expense_name : str = Field(max_length=64)
    expense_date: datetime.datetime = Field(default_factory=get_current_time_india)
    price : float
    expense_type_name : str = Field(default="Nill")
    category_name : str
    payment_mode_name : str
    additional_note : str = Field(max_length=140)

    @model_validator(mode="after")
    def validate_expense(self):
        validate_amount(self)
        self.expense_type_name = validate_transaction_type(self.expense_type_name)
        return self

class ExpenseResponse(ExpenseRequest):
    expense_id : int
    expense_type_id : int
    category_id : int
    payment_mode_id : int

    class Config:
        from_attributes = True

class BudgetFeedback(BaseModel):
    status: Literal["under", "over"]
    budget_amount: float
    spent: float
    remaining: float
    message: str

class ExpenseResponseWithBudgetFeedback(BaseModel):
    expense : ExpenseResponse
    budget_feedback: BudgetFeedback
    
class IncomeRequest(BaseModel):
    income_name : str = Field(max_length=64)
    recieved_date: datetime.datetime = Field(default_factory=get_current_time_india)
    amount : float
    income_type_name : str = Field(default="Nill")
    category_name : str
    payment_mode_name : str
    additional_note : str = Field(max_length=140)

    @model_validator(mode="after")
    def validate_income(self):
        validate_amount(self)
        self.income_type_name = validate_transaction_type(self.income_type_name)
        return self

class IncomeResponse(IncomeRequest):
    income_id : int
    income_type_id : int
    category_id : int
    payment_mode_id : int

    class Config:
        from_attributes = True

class TransactionQueryParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    transaction_id : Optional[int] = Field(None, description="Income ID or Expense ID")
    name : Optional[str] = Field(None, description = "Name of income or expense")
    exact_amount : Optional[int] = Field(None, description="Exact amount transaction")
    greater_amount : Optional[int] = Field(None, gt=0, description="Transactions greater than this amount")
    lower_amount : Optional[int] = Field(None, gt=0, description="Transactions smaller than this amount")
    date : Optional[datetime.date] = Field(None, description="Date of transaction")
    limit : Optional[int] = Field(20, description="No. of transactions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit