import datetime
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List
from zoneinfo import ZoneInfo

def get_current_time_india():
    return datetime.datetime.now(ZoneInfo("Asia/Kolkata"))

class billing_period(str, Enum):
    yearly = "yearly"
    half_yearly = "half_yearly"
    quaterly = "quaterly"
    weekly = "weekly"
    one_time = "one_time"
    monthly = "monthly"

class SubscriptionRequest(BaseModel):
    subscription_name : str = Field(max_length=64)
    amount : int = Field(gt=0)
    description : str = Field(max_length=140)
    currency : str = Field("INR", max_length=3)
    account_name : Optional[str] = Field(default=None, description="Name of account")
    billing_cycle : billing_period
    category_name : str
    expense_type_name : str
    payment_mode_name : str
    start_date : datetime.datetime = Field(default_factory=get_current_time_india)
    end_date : Optional[datetime.datetime] = Field(default=None)
    is_active : bool = Field(True)
    last_paid_at : datetime.datetime

class SubscriptionResponse(SubscriptionRequest):
    subscription_id : int
    category_id : int
    expense_type_id : int
    payment_mode_id : int
    account_id : Optional[int] = None
    last_paid_at : Optional[datetime.datetime] = None
    next_billing_date : datetime.datetime

    model_config = {
        "from_attributes": True 
    }

class PaginatedSubscriptionResponse(BaseModel):
    total_pages: int
    current_page: int
    total_subscriptions: int
    subscriptions: List[SubscriptionResponse]

    model_config = {
        "from_attributes" : True
    }

class SubscriptionOverview(BaseModel):
    total_subscription_last_30_days : float
    total_subscription_last_7_days : float
    total_subscription_current_month: float
    average_monthly_subscription : float
    average_weekly_subscription : float

class SubscriptionQueryParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    subscription_id : Optional[int] = Field(None, description="Subscription ID")
    name : Optional[str] = Field(None, description = "Name of subscription")
    exact_amount : Optional[int] = Field(None, description="Exact amount subscription")
    greater_amount : Optional[int] = Field(None, gt=0, description="Subscriptions greater than this amount")
    lower_amount : Optional[int] = Field(None, gt=0, description="Subscriptions smaller than this amount")
    start_date : Optional[datetime.date] = Field(None, description="Start date of subscription")
    end_date : Optional[datetime.date] = Field(None, description="End date of subscription")
    billing_date : Optional[datetime.date] = Field(None, description="Billing date of the subscription")
    limit : Optional[int] = Field(20, description="No. of subscriptions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")
    active_subscriptions : Optional[bool] = Field(None, description="All subscriptions which are not ended")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit



