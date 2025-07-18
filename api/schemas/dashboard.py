from pydantic import BaseModel, Field
from typing import Optional

class overviewResponse(BaseModel):
    total_income : float 
    total_expense : float
    total_budget : float 
    total_subscription : float 
    total_investment : float 