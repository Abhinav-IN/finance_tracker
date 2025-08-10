from api.tasks.compound_task import calculate_compound_growth
from api.schemas.investment import InvestmentType, InvestmentStatus
from api.database.session import SessionLocal
from api.models.investment_goal import InvestmentGoal
from api.models.investment import Investment
from celery import shared_task
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

def calculate_current_value(units: float, price_per_unit: float) -> float:
    return round(units * price_per_unit, 2)

def calculate_gain_or_loss(current_value: float, amount_invested: float) -> float:
    return round(current_value - amount_invested, 2)

def link_investments_to_goal(
    db: Session,
    goal: InvestmentGoal,
    user_id: int,
    investment_ids: List[int],
    applies_to_all: bool,
):
    if applies_to_all:
        all_investments = (
            db.query(Investment)
            .filter(Investment.user_id == user_id)
            .all()
        )
        goal.applies_to_all_investments = True
        goal.investments = all_investments
        db.commit()
        return all_investments
    else:
        investments = (
            db.query(Investment)
            .filter(Investment.user_id == user_id)
            .filter(Investment.id.in_(investment_ids))
            .all()
        )
        if len(investments) != len(investment_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Some investment IDs are invalid or not owned by the user.",
            )
        goal.applies_to_all_investments = False
        goal.investments = investments
        db.commit()
        return investments

@shared_task
def update_all_investment_goal_values():
    db: Session = SessionLocal()
    try:
        all_goals = db.query(InvestmentGoal).all()

        for goal in all_goals:
            if goal.applies_to_all_investments:
                investments = db.query(Investment).filter(
                    Investment.user_id == goal.user_id,
                    Investment.status.notin_([InvestmentStatus.fully_withdrawl, InvestmentStatus.matured])
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
            Investment.status.notin_([InvestmentStatus.fully_withdrawl, InvestmentStatus.matured])
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

def get_basic_data(investment_id: int, user_id: int, db : Session):
    investment = db.query(Investment).filter(Investment.investment_id == investment_id, Investment.user_id == user_id).first()
    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")
    
    return investment.investment_type, investment.account_linked
