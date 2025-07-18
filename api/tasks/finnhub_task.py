import re
import httpx
from api.core.config import settings
from fastapi import HTTPException, status
import yfinance as yf
from api.utils.currency_conversion import convert_currency
from celery import shared_task

BASE_URL = settings.finnhub_api_url


def extract_exchange(symbol: str) -> str:
    if symbol.endswith(".NS"):
        return "NSE"
    elif symbol.endswith(".BO"):
        return "BSE"
    elif "." not in symbol:
        return "NEEDS_LOOKUP"  
    else:
        return "None"  


def normalize_us_exchange(raw_exchange: str) -> str:
    raw = raw_exchange.strip().upper()
    if "NASDAQ" in raw:
        return "NASDAQ"
    elif "NEW YORK STOCK EXCHANGE" in raw or "NYSE" in raw:
        return "NYSE"
    else:
        return "None"  


def is_relevant_match(query: str, company: str, symbol: str) -> bool:
    query = query.lower()
    company = company.lower()
    symbol = symbol.lower()

    return (
        symbol.startswith(query) or
        company.startswith(query) or
        re.search(rf'\b{re.escape(query)}\b', company) is not None
    )


async def get_us_stock_exchange(symbol: str) -> str:
    url = settings.finnhub_us_exchange
    params = {
        "symbol": symbol,
        "token": settings.finnhub_api_key
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            return normalize_us_exchange(data.get("exchange", ""))
        except Exception:
            return "None"


async def search_company_symbols(company_name: str):
    url = f"{BASE_URL}/search"
    params = {
        "q": company_name,
        "token": settings.finnhub_api_key
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()

    results = []

    for item in data.get("result", []):
        symbol = item.get("symbol", "")
        company = item.get("description", "")

        if not is_relevant_match(company_name, company, symbol):
            continue

        exchange = extract_exchange(symbol)
        if exchange == "NEEDS_LOOKUP":
            exchange = await get_us_stock_exchange(symbol)

        if exchange in {"NSE", "BSE", "NASDAQ", "NYSE"}:
            results.append({
                "company": company,
                "symbol": symbol,
                "exchange": exchange
            })

    results.sort(key=lambda x: (
        0 if x["company"].lower().startswith(company_name.lower()) else 1,
        x["company"]
    ))

    if not results:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No relevant US or Indian stocks found.")

    return results

@shared_task
async def get_current_price_of_stock(
    ticker_symbol: str,
    exchange_symbol: str,
    to_currency: str = "INR"
) -> float | None:
    supported_exchanges = {"NSE", "BSE", "NASDAQ", "NYSE"}
    if exchange_symbol not in supported_exchanges:
        print(f"Unsupported exchange: {exchange_symbol}")
        return None

    current_price = None
    from_currency = "INR" if exchange_symbol in {"NSE", "BSE"} else "USD"

    try:
        yf_symbol = (
            f"{ticker_symbol}.NS" if exchange_symbol == "NSE"
            else f"{ticker_symbol}.BO" if exchange_symbol == "BSE"
            else ticker_symbol
        )
        print(f"Trying yfinance for symbol: {yf_symbol}")
        stock = yf.Ticker(yf_symbol)
        price = stock.info.get("regularMarketPrice")
        print(f"yfinance price for {yf_symbol}: {price}")
        if isinstance(price, (int, float)) and price > 0:
            current_price = float(price)
    except Exception as e:
        print(f"yfinance failed for {yf_symbol} with error: {e}")

    if current_price is None:
        try:
            finnhub_symbol = (
                f"{ticker_symbol}.{'NS' if exchange_symbol == 'NSE' else 'BO'}"
                if exchange_symbol in {"NSE", "BSE"}
                else ticker_symbol
            )
            url = f"{settings.finnhub_api_url}/quote"
            params = {"symbol": finnhub_symbol, "token": settings.finnhub_api_key}

            print(f"Trying Finnhub for symbol: {finnhub_symbol}")
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

            price = data.get("c")
            print(f"Finnhub price for {finnhub_symbol}: {price}")
            if isinstance(price, (int, float)) and price > 0:
                current_price = float(price)
        except Exception as e:
            print(f"Finnhub failed for {finnhub_symbol} with error: {e}")

    if current_price is not None:
        try:
            converted_price = convert_currency(current_price, from_currency, to_currency)
            print(f"Converted price from {from_currency} to {to_currency}: {converted_price}")
            return converted_price
        except Exception as e:
            print(f"Currency conversion failed: {e}")
            return None

    print("All sources failed to fetch price.")
    return None