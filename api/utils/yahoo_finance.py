import yfinance as yf
from datetime import datetime
from zoneinfo import ZoneInfo
from api.utils.currency_conversion import convert_currency


def get_ticker_currency(symbol: str) -> str:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return info.get("financialCurrency", "USD") 
    except Exception:
        return "USD"


def get_ticker_data(symbol: str, target_currency: str = "INR") -> dict:
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        if "regularMarketPrice" not in info:
            raise ValueError("Ticker data does not include 'regularMarketPrice'")

        current_price_per_unit = round(info["regularMarketPrice"], 2)
        source_currency = info.get("financialCurrency", "USD")

        current_price_per_unit = convert_currency(
            current_price_per_unit, source_currency, target_currency
        )

        return {
            "current_price_per_unit": current_price_per_unit,
            "last_synced_at": datetime.now(tz=ZoneInfo("Asia/Kolkata"))
        }

    except Exception as e:
        raise ValueError(f"Could not fetch ticker data: {str(e)}")
