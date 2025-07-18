from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.investment import Investment
from api.schemas.investment import InvestmentRequest, investmentResponse, InvestmentQueryParam, stockSuggestionQueryParam, InvestmentUpdateRequest
from api.utils.investment import calculate_compound_growth
from api.tasks.finnhub_task import search_company_symbols, get_current_price_of_stock
from api.tasks.finnhub_task import get_current_price_of_stock
from api.tasks.coingecko_task import get_current_crypto_price 
from datetime import datetime, time
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo


def calculate_current_value(units: float, price_per_unit: float) -> float:
    return round(units * price_per_unit, 2)

def calculate_gain_or_loss(current_value: float, amount_invested: float) -> float:
    return round(current_value - amount_invested, 2)

async def create_investment_service(
    user_investment: InvestmentRequest,
    user: dict = Depends(require_roles),
    db: Session = Depends(get_db)
):
    last_synced_at = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

    curr_price_per_unit = None
    gainOrLoss = None
    curr_value = None

    if user_investment.investment_type == "mutual_fund":
        curr_price_per_unit = user_investment.buy_price_per_unit
        curr_value = calculate_current_value(user_investment.units, curr_price_per_unit)
        gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    elif user_investment.investment_type in ["stock", "etf"]:
        try:
            curr_price_per_unit = await get_current_price_of_stock(
                user_investment.ticker_symbol,
                user_investment.exchange_symbol
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        if curr_price_per_unit:
            curr_value = calculate_current_value(user_investment.units, curr_price_per_unit)
            gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    elif user_investment.investment_type == "crypto":
        try:
            curr_price_per_unit = await get_current_crypto_price(user_investment.ticker_symbol)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Crypto price error: {str(e)}"
            )
        if curr_price_per_unit:
            curr_value = calculate_current_value(user_investment.units, curr_price_per_unit)
            gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    elif user_investment.investment_type in ["fd", "bond"]:
        curr_value = calculate_compound_growth(
            principal=user_investment.amount_invested,
            interest_rate=user_investment.interest_rate,
            start_date=user_investment.investment_date,
            end_date=last_synced_at,
            frequency=user_investment.compounding_frequency
        )
        gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    else:
        curr_price_per_unit = user_investment.buy_price_per_unit or 0.0
        curr_value = calculate_current_value(user_investment.units or 1, curr_price_per_unit)
        gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    new_investment = Investment(
        user_id=user["id"],
        investment_name=user_investment.investment_name,
        investment_type=user_investment.investment_type,
        investment_date=user_investment.investment_date,
        description=user_investment.description,
        platform=user_investment.platform,
        ticker_symbol=getattr(user_investment, "ticker_symbol", None),
        exchange_symbol=getattr(user_investment, "exchange_symbol", None),
        amount_invested=user_investment.amount_invested,
        units=getattr(user_investment, "units", None),
        buy_price_per_unit=getattr(user_investment, "buy_price_per_unit", None),
        maturity_date=getattr(user_investment, "maturity_date", None),
        interest_rate=getattr(user_investment, "interest_rate", None),
        compounding_frequency=getattr(user_investment, "compounding_frequency", None),
        current_price_per_unit=curr_price_per_unit,
        current_value=curr_value,
        is_active=user_investment.is_active,
        last_synced_at=last_synced_at,
        gain_or_loss=gainOrLoss
    )

    db.add(new_investment)
    try:
        db.commit()
        db.refresh(new_investment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong in creating investment"
        )

    return investmentResponse.model_validate(new_investment)

def get_investment_service(filter_query: InvestmentQueryParam,
                            user: dict = Depends(require_roles("user", "admin")),
                            db: Session = Depends(get_db)):
    curr_query = db.query(Investment).filter(Investment.user_id == user["id"])
    if filter_query.investment_id:
        curr_query = curr_query.filter(Investment.investment_id == filter_query.investment_id)
    if filter_query.investment_name:
        curr_query = curr_query.filter(Investment.investment_name.ilike(filter_query.investment_name.strip()))
    if filter_query.type:
        curr_query = curr_query.filter(Investment.investment_type.ilike(filter_query.type.strip()))
    if filter_query.investment_date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.investment_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.investment_date, time.max).replace(tzinfo=ist)
        curr_query = curr_query.filter(Investment.investment_date.between(start_of_day, end_of_day))
    if filter_query.platform:
        curr_query = curr_query.filter(Investment.platform.ilike(filter_query.platform.strip()))
    if filter_query.exact_amount:
        curr_query = curr_query.filter(Investment.amount_invested == filter_query.exact_amount)
    if filter_query.greater_amount:
        curr_query = curr_query.filter(Investment.amount_invested > filter_query.greater_amount)
    if filter_query.lower_amount:
        curr_query = curr_query.filter(Investment.amount_invested < filter_query.lower_amount)
    if filter_query.active_investments:
        curr_query = curr_query.filter(Investment.is_active == True)
    if filter_query.search:
        curr_query = curr_query.filter(Investment.description.ilike(f"%{filter_query.search}%"))

    curr_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit)
    return [investmentResponse.model_validate(i) for i in curr_query.all()]

async def update_investment_service(investment_id: int,
                                    user_investment: InvestmentUpdateRequest,
                                    user: dict = Depends(require_roles("admin", "user")),
                                    db: Session = Depends(get_db)):
    curr_investment_query = db.query(Investment).filter(
        Investment.investment_id == investment_id,
        Investment.user_id == user["id"]
    )
    curr_investment = curr_investment_query.first()

    if not curr_investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment Not Found")

    last_synced_at = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    
    updated_curr_price_per_unit = None
    updated_current_value = None
    updated_gainOrLoss = None

    if user_investment.investment_type == "mutual_fund":
        updated_curr_price_per_unit = user_investment.current_price_per_unit
        updated_current_value = calculate_current_value(user_investment.units, updated_curr_price_per_unit)
        updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    elif user_investment.investment_type in ["stock", "etf"]:
        if user_investment.current_price_per_unit and user_investment.current_price_per_unit != curr_investment.current_price_per_unit:
            updated_curr_price_per_unit = user_investment.current_price_per_unit
        else:
            try:
                curr_price_per_unit = await get_current_price_of_stock(
                user_investment.ticker_symbol,
                user_investment.exchange_symbol
                )
            except ValueError as e:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        
        updated_curr_price_per_unit = curr_price_per_unit if curr_price_per_unit is not None else curr_investment.current_price_per_unit
        if updated_curr_price_per_unit:
            updated_current_value = calculate_current_value(user_investment.units, updated_curr_price_per_unit)
            updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    elif user_investment.investment_type == "crypto":
        if user_investment.current_price_per_unit and user_investment.current_price_per_unit != curr_investment.current_price_per_unit:
            updated_curr_price_per_unit = user_investment.current_price_per_unit
        else:
            try:
                curr_price_per_unit = await get_current_crypto_price(user_investment.ticker_symbol)
            except ValueError as e:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Crypto price error: {str(e)}"
                )
        updated_curr_price_per_unit = curr_price_per_unit if curr_price_per_unit is not None else curr_investment.current_price_per_unit
        if updated_curr_price_per_unit:
            updated_current_value = calculate_current_value(user_investment.units, updated_curr_price_per_unit)
            updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    elif user_investment.investment_type in ["fd", "bond"]:
        updated_current_value = calculate_compound_growth(
            principal=user_investment.amount_invested,
            interest_rate=user_investment.interest_rate,
            start_date=user_investment.investment_date,
            end_date=last_synced_at,
            frequency=user_investment.compounding_frequency
        )
        updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    else:
        updated_curr_price_per_unit = user_investment.current_price_per_unit
        updated_current_value = calculate_current_value(user_investment.units or 1, updated_curr_price_per_unit)
        updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)



    curr_investment_query.update({
        "investment_name": user_investment.investment_name,
        "investment_type": user_investment.investment_type,
        "investment_date": user_investment.investment_date,
        "description": user_investment.description,
        "platform": user_investment.platform,
        "ticker_symbol": getattr(user_investment, "ticker_symbol", None),
        "amount_invested": user_investment.amount_invested,
        "units": getattr(user_investment, "units", None),
        "buy_price_per_unit": getattr(user_investment, "buy_price_per_unit", None),
        "maturity_date": getattr(user_investment, "maturity_date", None),
        "interest_rate": getattr(user_investment, "interest_rate", None),
        "compounding_frequency": getattr(user_investment, "compounding_frequency", None),
        "current_price_per_unit": updated_curr_price_per_unit,
        "current_value": updated_current_value,
        "is_active": user_investment.is_active,
        "last_synced_at": last_synced_at,
        "gain_or_loss": updated_gainOrLoss
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(curr_investment)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating investment")

    return investmentResponse.model_validate(curr_investment)



def delete_investment_service(investment_id: int,
                               user: dict = Depends(require_roles("user", "admin")),
                               db: Session = Depends(get_db)):
    investment = db.query(Investment).filter(Investment.investment_id == investment_id).first()

    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    if user["role"] != "admin" and investment.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own investment")

    db.delete(investment)
    db.commit()
    return

async def suggest_symbols(filter_query : stockSuggestionQueryParam,
                          user : dict = Depends(get_db)):
    try:
        results = await search_company_symbols(filter_query.company_name)
        if not results:
            return {"message": "No relevant US or Indian stocks found."}
        return results
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
