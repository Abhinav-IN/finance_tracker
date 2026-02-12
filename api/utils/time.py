from datetime import datetime
from zoneinfo import ZoneInfo

IST = ZoneInfo("Asia/Kolkata")

def ist_now() -> datetime:
    return datetime.now(IST)