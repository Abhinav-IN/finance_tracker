import requests
from api.core.config import settings

def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    if from_currency == to_currency:
        return round(amount, 2)

    try:
        params = {
            "base_currency": from_currency,
            "currencies": to_currency
        }
        headers = {
            "apikey": settings.currency_api_key
        }

        response = requests.get(settings.currency_api_url, params=params, headers=headers)
        data = response.json()

        rate = data.get("data", {}).get(to_currency, {}).get("value")
        if rate is None:
            raise ValueError(f"CurrencyAPI error: {data}")

        return round(amount * rate, 2)

    except Exception as e:
        raise ValueError(f"Currency conversion error: {str(e)}")
