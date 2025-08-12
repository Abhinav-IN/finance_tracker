import datetime
from enum import Enum
from typing import Optional, Union, Literal, Annotated, List
from pydantic import BaseModel, Field

class InvestmentType(str, Enum):
    stock = "stock"
    crypto = "crypto"
    mutual_fund = "mutual_fund"
    etf = "etf"
    fd = "fd"
    bond = "bond"

class InvestmentStatus(str, Enum):
    active = "active"
    partially_withdrawl = "partially_withdrawl"
    fully_withdrawl = "fully_withdrawl"
    matured = "matured"

class CompoundingFrequency(str, Enum):
    yearly = "annually"
    semi_annually = "semi_annually"
    quarterly = "quarterly"
    monthly = "monthly"
    weekly = "weekly"
    none = "none"

class BaseInvestmentRequest(BaseModel):
    investment_name: str = Field(..., max_length=104)
    investment_type: InvestmentType
    investment_date: datetime.datetime
    description: Optional[str] = Field(default=None, max_length=255)
    platform: str = Field(..., max_length=104)
    amount_invested: float = Field(gt=0)
    status: InvestmentStatus = InvestmentStatus.active  
    withdrawl_amount: Optional[float] = 0               
    withdrawl_date: Optional[datetime.datetime] = None 
    account_name: Optional[str] = None

class TickerBasedInvestment(BaseInvestmentRequest):
    units: float = Field(gt=0)
    units_withdrawl : Optional[float] = 0.0
    buy_price_per_unit: float = Field(gt=0)
    current_price_per_unit: float = Field(gt=0)
    maturity_date: Optional[datetime.datetime] = None  

class StockInvestmentRequest(TickerBasedInvestment):
    investment_type: Literal["stock"]

class MutualFundRequest(TickerBasedInvestment):
    investment_type: Literal["mutual_fund"]

class ETFRequest(TickerBasedInvestment):
    investment_type: Literal["etf"]

class CryptoInvestmentRequest(TickerBasedInvestment):
    investment_type: Literal["crypto"]

class FDInvestmentRequest(BaseInvestmentRequest):
    investment_type: Literal["fd"]
    maturity_date: datetime.datetime
    interest_rate: float
    compounding_frequency: CompoundingFrequency

class BondInvestmentRequest(BaseInvestmentRequest):
    investment_type: Literal["bond"]
    maturity_date: datetime.datetime
    interest_rate: float
    compounding_frequency: CompoundingFrequency = CompoundingFrequency.yearly

InvestmentRequest = Annotated[
    Union[
        StockInvestmentRequest,
        MutualFundRequest,
        ETFRequest,
        CryptoInvestmentRequest,
        FDInvestmentRequest,
        BondInvestmentRequest
    ],
    Field(discriminator="investment_type")
]

class investmentResponse(BaseInvestmentRequest):
    investment_id: int
    current_price_per_unit: Optional[float] = None
    current_value: Optional[float] = None
    last_synced_at: datetime.datetime
    gain_or_loss: Optional[float] = None
    units: Optional[float] = None
    units_withdrawl : Optional[float] = 0.0
    buy_price_per_unit: Optional[float] = None
    maturity_date: Optional[datetime.datetime] = None
    interest_rate: Optional[float] = None
    compounding_frequency: Optional[CompoundingFrequency] = None
    account_linked: Optional[int] = None

    model_config = {"from_attributes": True}

class InvestmentQueryParam(BaseModel):
    page: int = Field(1, ge=1)
    investment_id: Optional[int] = None
    investment_name: Optional[str] = None
    type: Optional[str] = None
    investment_date: Optional[datetime.date] = None
    platform: Optional[str] = None
    exact_amount: Optional[int] = None
    greater_amount: Optional[int] = Field(None, gt=0)
    lower_amount: Optional[int] = Field(None, gt=0)
    limit: Optional[int] = Field(20)
    search: Optional[str] = None

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit

class InvestmentUpdateRequest(BaseModel):
    investment_name: str 
    investment_type: str   
    investment_date: datetime.date
    description: str 
    platform: str
    amount_invested: float 
    units: Optional[float] = None
    units_withdrawl : Optional[float] = 0.0
    buy_price_per_unit: Optional[float] = None

    current_price_per_unit: Optional[float] = None  

    maturity_date: Optional[datetime.date] = None
    interest_rate: Optional[float] = None
    compounding_frequency: Optional[str] = None

    account_name: Optional[str] = None

    status: InvestmentStatus 
    withdrawl_amount: Optional[float] = 0               
    withdrawl_date: Optional[datetime.datetime] = None 


    model_config = {"from_attributes": True}

class InvestmentWithdrawalRequest(BaseModel):
    investment_id: int
    withdraw_amount: float = Field(..., description="Amount to withdraw in ₹")
    withdrawal_date: datetime.date

class PaginatedInvestmentResponse(BaseModel):
    total_pages: int
    current_page: int
    total_investments: int
    investments: List[investmentResponse]

    model_config = {
        "from_attributes": True
    }