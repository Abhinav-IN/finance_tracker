import datetime
from enum import Enum
from typing import Optional, Union, Literal, Annotated
from pydantic import BaseModel, Field

# === Enum Definitions ===
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

# === Base Request Schema ===
class BaseInvestmentRequest(BaseModel):
    investment_name: str = Field(..., max_length=104)
    investment_type: InvestmentType
    investment_date: datetime.datetime
    description: Optional[str] = Field(default=None, max_length=255)
    platform: str = Field(..., max_length=104)
    amount_invested: float = Field(gt=0)
    is_active: bool

# === Specific Investment Types ===
class StockInvestmentRequest(BaseInvestmentRequest):
    investment_type: Literal["stock"]
    ticker_symbol: str = Field(..., min_length=2)
    units: float = Field(gt=0)
    buy_price_per_unit: float = Field(gt=0)
    maturity_date: Optional[datetime.datetime] = None

class MutualFundRequest(StockInvestmentRequest):
    investment_type: Literal["mutual_fund"]

class ETFRequest(StockInvestmentRequest):
    investment_type: Literal["etf"]

class CryptoRequest(StockInvestmentRequest):
    investment_type: Literal["crypto"]

class FDInvestmentRequest(BaseInvestmentRequest):
    investment_type: Literal["fd"]
    maturity_date: datetime.datetime
    interest_rate: float  # ✅ Add to model
    compounding_frequency: CompoundingFrequency  # ✅ Add to model

class BondInvestmentRequest(BaseInvestmentRequest):
    investment_type: Literal["bond"]
    maturity_date: datetime.datetime
    interest_rate: float  # ✅ Add to model

# ✅ Final Discriminated Union with Autocomplete Support
InvestmentRequest = Annotated[
    Union[
        StockInvestmentRequest,
        MutualFundRequest,
        ETFRequest,
        CryptoRequest,
        FDInvestmentRequest,
        BondInvestmentRequest
    ],
    Field(discriminator="investment_type")
]

# === Response Schema ===
class investmentResponse(BaseInvestmentRequest):
    investment_id: int
    current_price_per_unit: Optional[float] = None
    current_value: float
    last_synced_at: datetime.datetime
    gain_or_loss: Optional[float] = None
    ticker_symbol: Optional[str] = None  # for stock/mf/etf/crypto
    units: Optional[float] = None
    buy_price_per_unit: Optional[float] = None
    maturity_date: Optional[datetime.datetime] = None
    interest_rate: Optional[float] = None  # for FD/bond
    compounding_frequency: Optional[CompoundingFrequency] = None  # for FD only

    model_config = {"from_attributes": True}

# === Query Params ===
class InvestmentQueryParam(BaseModel):
    page: int = Field(1, ge=1)
    investment_id: Optional[int] = None
    investment_name: Optional[str] = None
    asset_name: Optional[str] = None
    type: Optional[str] = None
    investment_date: Optional[datetime.date] = None
    platform: Optional[str] = None
    exact_amount: Optional[int] = None
    greater_amount: Optional[int] = Field(None, gt=0)
    lower_amount: Optional[int] = Field(None, gt=0)
    limit: Optional[int] = Field(20)
    search: Optional[str] = None
    active_investments: Optional[bool] = None

    @property
    def get_offset(self):
        return (self.page - 1) * self.limit
