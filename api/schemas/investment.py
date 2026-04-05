import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from api.utils.enums import InvestmentStatus, InvestmentType

class InvestmentBase(BaseModel):
    name: str = Field(..., max_length=100)
    investment_type: InvestmentType
    platform: str = Field(..., max_length=100)
    amount: float = Field(..., gt=0)
    units: Optional[float] = Field(default=None, gt=0)
    buy_price: Optional[float] = Field(default=None, gt=0)
    date: datetime.datetime
    maturity_date: Optional[datetime.datetime] = None

class InvestmentCreateRequest(InvestmentBase):
    status: InvestmentStatus = InvestmentStatus.ACTIVE

class InvestmentUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    platform: Optional[str] = Field(None, max_length=100)
    amount: Optional[float] = Field(None, gt=0)
    units: Optional[float] = Field(None, gt=0)
    buy_price: Optional[float] = Field(None, gt=0)
    date: Optional[datetime.datetime] = None
    maturity_date: Optional[datetime.datetime] = None
    status: Optional[InvestmentStatus] = None

class InvestmentResponse(InvestmentBase):
    id: int
    status: InvestmentStatus
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    pnl: Optional[float] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}

class InvestmentPriceCreateRequest(BaseModel):
    price: float = Field(..., gt=0)
    recorded_at: Optional[datetime.datetime] = None

class InvestmentPriceResponse(BaseModel):
    id: int
    price: float
    recorded_at: datetime.datetime

    model_config = {"from_attributes": True}

class InvestmentQueryParams(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(20, ge=1)
    investment_type: Optional[InvestmentType] = None
    platform: Optional[str] = None
    status: Optional[InvestmentStatus] = None
    min_amount: Optional[float] = Field(None, gt=0)
    max_amount: Optional[float] = Field(None, gt=0)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

class PaginatedInvestmentResponse(BaseModel):
    total: int
    page: int
    limit: int
    data: List[InvestmentResponse]