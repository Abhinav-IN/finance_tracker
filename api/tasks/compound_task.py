from datetime import datetime
from zoneinfo import ZoneInfo
from api.schemas.investment import CompoundingFrequency

def calculate_compound_growth(principal: float, interest_rate: float, 
                               start_date: datetime, end_date: datetime,
                               frequency: CompoundingFrequency) -> float:
    tz = ZoneInfo("Asia/Kolkata")
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=tz)
    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=tz)

    freq_map = {
        CompoundingFrequency.yearly: 1,
        CompoundingFrequency.semi_annually: 2,
        CompoundingFrequency.quarterly: 4,
        CompoundingFrequency.monthly: 12,
        CompoundingFrequency.weekly: 52,
        CompoundingFrequency.none: 1
    }

    r = interest_rate / 100
    n = freq_map.get(frequency, 1)
    days = (end_date - start_date).days
    t = max(days / 365, 0)

    return round(principal * ((1 + (r / n)) ** (n * t)), 2)
