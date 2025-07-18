import datetime
from enum import Enum
from typing import Optional, Union, Literal, Annotated
from pydantic import BaseModel, Field

class InvestmentType(str, Enum):
    stock = "stock"
    crypto = "crypto"
    mutual_fund = "mutual_fund"
    etf = "etf"
    fd = "fd"
    bond = "bond"

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
    is_active: bool

class TickerBasedInvestment(BaseInvestmentRequest):
    ticker_symbol: str = Field(..., min_length=2)
    exchange_symbol: str = Field(..., min_length=2)
    units: float = Field(gt=0)
    buy_price_per_unit: float = Field(gt=0)
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
    ticker_symbol: Optional[str] = None
    exchange_symbol: Optional[str] = None
    units: Optional[float] = None
    buy_price_per_unit: Optional[float] = None
    maturity_date: Optional[datetime.datetime] = None
    interest_rate: Optional[float] = None
    compounding_frequency: Optional[CompoundingFrequency] = None

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
    limit: Optional[int] = Field(5)
    search: Optional[str] = None
    active_investments: Optional[bool] = None

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit

class stockSuggestionQueryParam(BaseModel):
    company_name: str 

class SymbolSuggestionResponse(BaseModel):
    company: str
    symbol: str
    exchange: str

    model_config = {"from_attributes": True}

class InvestmentUpdateRequest(BaseModel):
    investment_name: str 
    investment_type: str   
    investment_date: datetime.date
    description: str 
    platform: str

    ticker_symbol: Optional[str] = None
    exchange_symbol: Optional[str] = None

    amount_invested: float 
    units: Optional[float] = None
    buy_price_per_unit: Optional[float] = None

    current_price_per_unit: Optional[float] = None  

    maturity_date: Optional[datetime.date] = None
    interest_rate: Optional[float] = None
    compounding_frequency: Optional[str] = None

    is_active: Optional[bool] = True

    model_config = {"from_attributes": True}
