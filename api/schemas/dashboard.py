from api.utils.enums import TransactionDirection
from datetime import date
from decimal import Decimal
from pydantic import BaseModel

class overviewResponse(BaseModel):
    total_income : float 
    total_expense : float
    total_budget : float 
    total_subscription : float 
    total_investment : float 

class transaction_record(BaseModel):
    date : date
    total_transaction : Decimal