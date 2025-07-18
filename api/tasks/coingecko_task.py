import httpx
from api.utils.currency_conversion import convert_currency
from api.core.config import settings

COINGECKO_URL = settings.coingecko_api_url

SYMBOL_MAP = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "BNB": "binancecoin",
    "ADA": "cardano",
    "DOGE": "dogecoin",
}

async def get_current_crypto_price(
    symbol: str,
    to_currency: str = "INR"
) -> float:
    symbol = symbol.upper()
    coin_id = SYMBOL_MAP.get(symbol)
    if not coin_id:
        raise ValueError(f"Unsupported crypto symbol: {symbol}")

    async with httpx.AsyncClient() as client:
        resp = await client.get(
            COINGECKO_URL,
            params={"ids": coin_id, "vs_currencies": "usd"}
        )
        resp.raise_for_status()
        data = resp.json()

    usd_price = data.get(coin_id, {}).get("usd")
    if usd_price is None:
        raise ValueError(f"Price not found for {symbol}")

    return convert_currency(usd_price, from_currency="USD", to_currency=to_currency)
