from api.models.investment import Investment
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


def calculate_current_value(units: float, price_per_unit: float) -> float:
    return round(units * price_per_unit, 2)

def calculate_gain_or_loss(current_value: float, amount_invested: float) -> float:
    return round(current_value - amount_invested, 2)

def get_basic_data(investment_id: int, user_id: int, db : Session):
    investment = db.query(Investment).filter(Investment.id == investment_id, Investment.user_id == user_id).first()
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")
    
    return investment.investment_type
