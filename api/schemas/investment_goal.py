from pydantic import BaseModel, Field
from typing import List, Optional
import datetime

class investment_goal_request(BaseModel):
    goal_name: str
    goal_amount: float = Field(gt=0)
    start_date: datetime.date
    end_date: datetime.date
    applies_to_all_investments: bool = Field(True)
    investment_ids: Optional[List[int]] = None
    description: str = Field(max_length=255)

class investment_goal_response(BaseModel):
    goal_id: int
    goal_name: str
    goal_amount: float
    start_date: datetime.date
    end_date: datetime.date
    applies_to_all_investments: bool
    investment_ids: Optional[List[int]]
    description: Optional[str]
    current_value: float

    model_config = {
        "from_attributes": True 
    }

class investment_goal_status_response(BaseModel):
    goal_id: int
    goal_name: str
    goal_amount: float
    current_value: float
    remaining: float
    start_date: datetime.date
    end_date: datetime.date
    status: str  # "active", "completed", "expired"
    message: Optional[str] = None
    
    model_config = {
        "from_attributes": True 
    }

class investmentGoalQueryParam(BaseModel):
    page: int = Field(1, ge=1, description="Page number starting from 1")
    goal_id: Optional[int] = Field(None, description="Investment goal ID")
    goal_name: Optional[str] = Field(None, description="Name of investment goal")
    exact_amount: Optional[int] = Field(None, description="Exact amount of investment goal")
    greater_amount: Optional[int] = Field(None, gt=0, description="investment goal greater than this amount")
    lower_amount: Optional[int] = Field(None, gt=0, description="investment goal smaller than this amount")
    start_date: Optional[datetime.date] = Field(None, description="Start date of investment goal")
    end_date: Optional[datetime.date] = Field(None, description="End date of investment goal")
    limit: Optional[int] = Field(20, description="No. of subscriptions visible at a time")
    search: Optional[str] = Field(None, description="Search by keywords")
    active_goals: Optional[bool] = Field(None, description="All goals which are not completed")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit
