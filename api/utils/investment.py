from api.utils.yahoo_finance import get_ticker_data
from api.tasks.compound_task import calculate_compound_growth
from api.schemas.investment import InvestmentType
from api.database.session import get_db, SessionLocal
from api.models.investment_goal import InvestmentGoal
from api.models.investment import Investment
from celery import shared_task
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

def sync_all_investments():
    db = next(get_db())

    all_investments = db.query(Investment).filter(Investment.is_active == True).all()

    for investment in all_investments:
        try:
            if not investment.ticker_symbol:
                continue

            data = get_ticker_data(investment.ticker_symbol)
            current_price = data["current_price_per_unit"]
            current_value = round((investment.units or 0) * current_price, 2)

            investment.current_price_per_unit = current_price
            investment.current_value = current_value
            investment.last_synced_at = datetime.now(ZoneInfo("Asia/Kolkata"))
        except Exception as e:
            continue

    db.commit()

def link_investments_to_goal(goal_id: int, investment_ids: list[int], user_id: int, db: Session):
    goal = db.query(InvestmentGoal).filter_by(goal_id=goal_id, user_id=user_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found or not authorized")

    goal.investments = []

    investments = db.query(Investment).filter(
        Investment.investment_id.in_(investment_ids),
        Investment.user_id == user_id
    ).all()

    if len(investments) != len(set(investment_ids)):
        raise HTTPException(status_code=400, detail="One or more investment IDs are invalid or not yours")

    goal.investments.extend(investments)
    goal.applies_to_all_investments = False
    db.commit()

@shared_task
def update_all_investment_goal_values():
    db: Session = SessionLocal()
    try:
        all_goals = db.query(InvestmentGoal).all()

        for goal in all_goals:
            if goal.applies_to_all_investments:
                investments = db.query(Investment).filter(
                    Investment.user_id == goal.user_id,
                    Investment.is_active == True
                ).all()
            else:
                investments = goal.investments

            total = sum(inv.current_value or 0 for inv in investments)
            goal.current_value = total

        db.commit()
    finally:
        db.close()

@shared_task
def update_fd_and_bond_values():
    db: Session = SessionLocal()
    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)

    try:
        investments = db.query(Investment).filter(
            Investment.investment_type.in_([InvestmentType.fd, InvestmentType.bond]),
            Investment.is_active == True
        ).all()

        for inv in investments:
            curr_val = calculate_compound_growth(
                principal=inv.amount_invested,
                interest_rate=inv.interest_rate,
                start_date=inv.investment_date,
                end_date=now,
                frequency=inv.compounding_frequency
            )

            inv.current_value = curr_val
            inv.gain_or_loss = round(curr_val - inv.amount_invested, 2)
            inv.last_synced_at = now

        db.commit()

    except Exception as e:
        db.rollback()
        print(f"[FD/Bond Update Error] {str(e)}")
    finally:
        db.close()
