from api.utils.enums import BillingPeriod
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List

class SubscriptionCreate(BaseModel):
    name: str = Field(max_length=64)
    amount: float = Field(gt=0)
    description: str = Field(max_length=140)
    currency: str = Field(default="INR", max_length=3)
    billing_period: BillingPeriod
    category_name: str
    transaction_type_name: str
    payment_mode_name: str
    account_name: Optional[str] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    last_paid_at: Optional[datetime] = None
    is_active: bool = True

class SubscriptionResponse(BaseModel):
    id: int
    name: str
    amount: float
    description: str
    currency: str
    billing_period: BillingPeriod
    start_date: datetime
    end_date: Optional[datetime]
    next_billing_date: Optional[datetime]
    last_paid_at: Optional[datetime]
    category_id: int
    transaction_type_id: int
    payment_mode_id: int
    account_id: Optional[int]
    is_active: bool

    model_config = {"from_attributes": True}

class PaginatedSubscriptionResponse(BaseModel):
    total_pages: int
    current_page: int
    total_subscriptions: int
    subscriptions: List[SubscriptionResponse]

    model_config = {"from_attributes" : True}

class SubscriptionOverview(BaseModel):
    total_subscription_last_30_days : float
    total_subscription_last_7_days : float
    total_subscription_current_month: float
    average_monthly_subscription : float
    average_weekly_subscription : float

class SubscriptionQueryParam(BaseModel):
    page : int = Field(1, ge=1, description="Page number starting from 1")
    id : Optional[int] = Field(None, description="Subscription ID")
    name : Optional[str] = Field(None, description = "Name of subscription")
    exact_amount : Optional[int] = Field(None, description="Exact amount subscription")
    greater_amount : Optional[int] = Field(None, gt=0, description="Subscriptions greater than this amount")
    lower_amount : Optional[int] = Field(None, gt=0, description="Subscriptions smaller than this amount")
    start_date : Optional[datetime] = Field(None, description="Start date of subscription")
    end_date : Optional[datetime] = Field(None, description="End date of subscription")
    billing_date : Optional[datetime] = Field(None, description="Billing date of the subscription")
    limit : Optional[int] = Field(20, description="No. of subscriptions visible at a time")
    search : Optional[str] = Field(None, description="Search by keywords")
    active_subscriptions : Optional[bool] = Field(None, description="All subscriptions which are not ended")

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit



