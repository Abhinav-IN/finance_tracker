from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from api.database.session import get_db
from api.models.investment import Investment
from api.models.investment_price import InvestmentPrice
from api.schemas.investment_price import InvestmentPriceCreate

def create_investment_price_service(data: InvestmentPriceCreate, user_id: int, db: Session):
    investment = db.query(Investment).filter(
        Investment.id == data.investment_id,
        Investment.user_id == user_id
    ).first()

    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    price = InvestmentPrice(
        investment_id=data.investment_id,
        price_per_unit=data.price_per_unit,
        total_value=data.total_value
    )

    db.add(price)
    try:
        db.commit()
        db.refresh(price)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creating price")

    return price

def get_investment_price_history_service(investment_id: int, user_id: int, db: Session):
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.user_id == user_id
    ).first()

    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    return investment.prices
