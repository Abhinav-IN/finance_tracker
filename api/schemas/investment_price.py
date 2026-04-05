from datetime import datetime
from pydantic import BaseModel

class InvestmentPriceCreate(BaseModel):
    investment_id: int
    price_per_unit: float
    total_value: float | None = None

class InvestmentPriceResponse(BaseModel):
    id: int
    investment_id: int
    price_per_unit: float
    total_value: float | None
    recorded_at: datetime

    class Config:
        from_attributes = True
