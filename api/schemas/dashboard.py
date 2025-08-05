from datetime import date
from pydantic import BaseModel

class overviewResponse(BaseModel):
    total_income : float 
    total_expense : float
    total_budget : float 
    total_subscription : float 
    total_investment : float 

class expense_record(BaseModel):
    date : date
    total_expense : float

class income_record(BaseModel):
    date : date
    total_income : float
