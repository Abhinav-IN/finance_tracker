from api.utils.validator import validate_date_and_amount
from datetime import date
from pydantic import BaseModel, Field, model_validator, RootModel
from typing import Optional, List

class budgetRequest(BaseModel):
    amount : int
    start_date : date
    end_date : date
    category_name : str

    @model_validator(mode='after')
    def validate(self):
        return validate_date_and_amount(self)

class budgetResponse(budgetRequest):
    id : int
    category_id : int

    model_config = {"from_attributes" : True}
    
class BudgetStatusOut(BaseModel):
    category_id: int
    category_name: str
    status: str  # "under" | "over"
    budget_amount: float
    spent: float
    remaining: float
    message: str


class AllBudgetStatusResponse(RootModel[List[BudgetStatusOut]]):
    pass

class budgetQueryParam(BaseModel):
    id : Optional[int] = Field(None, gt=0, description="ID of budget")
    start_date : Optional[date] = Field(None, description="Starting date of budget")
    end_date : Optional[date] = Field(None, description="ENding date of budget")
    category_name : Optional[str] = Field(None, description="Name of category associated iwth budget")
    greater_budget_amount : Optional[int] = Field(None, gt=0, description="Budgets greater than this amount")
    lower_budget_amount : Optional[int] = Field(None, gt=0, description="Budgets lower than this amount")
    exact_budget_amount : Optional[int] = Field(None, gt=0, description="Budgets exactly equal to this amount")
    page : Optional[int] = Field(1, ge=1, description="Page number starting from 1")
    limit : Optional[int] = Field(10, gt=0, description="No. of budgets per page")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit