from api.tasks.compound_task import calculate_compound_growth
from api.schemas.investment import InvestmentType
from api.database.session import SessionLocal
from api.models.investment_goal import InvestmentGoal
from api.models.investment import Investment
from celery import shared_task
from datetime import datetime
from fastapi import HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo
from api.tasks.finnhub_task import get_current_price_of_stock
from api.tasks.coingecko_task import get_current_crypto_price
from api.services.investment_service import calculate_current_value, calculate_gain_or_loss
import asyncio


@shared_task
def sync_stock_and_etf_prices():
    db = SessionLocal()
    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        stocks = db.query(Investment).filter(
            Investment.is_active == True,
            Investment.investment_type.in_([InvestmentType.stock, InvestmentType.etf])
        ).all()

        for inv in stocks:
            try:
                if not inv.ticker_symbol or not inv.exchange_symbol:
                    continue

                price = loop.run_until_complete(
                    get_current_price_of_stock(inv.ticker_symbol, inv.exchange_symbol)
                )

                if price:
                    curr_value = calculate_current_value(inv.units or 0, price)
                    gain_loss = calculate_gain_or_loss(curr_value, inv.amount_invested)

                    inv.current_price_per_unit = price
                    inv.current_value = curr_value
                    inv.gain_or_loss = gain_loss
                    inv.last_synced_at = now  

            except Exception as e:
                print(f"[Stock Sync Error] {inv.investment_name}: {e}")
                continue

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Stock Sync DB Error] {e}")
    finally:
        db.close()
        loop.close()


@shared_task
def sync_crypto_prices():
    db = SessionLocal()
    ist = ZoneInfo("Asia/Kolkata")
    now = datetime.now(ist)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        cryptos = db.query(Investment).filter(
            Investment.is_active == True,
            Investment.investment_type == InvestmentType.crypto
        ).all()

        for inv in cryptos:
            try:
                if not inv.ticker_symbol:
                    continue

                price = loop.run_until_complete(get_current_crypto_price(inv.ticker_symbol))

                if price:
                    curr_value = calculate_current_value(inv.units or 0, price)
                    gain_loss = calculate_gain_or_loss(curr_value, inv.amount_invested)

                    inv.current_price_per_unit = price
                    inv.current_value = curr_value
                    inv.gain_or_loss = gain_loss
                    inv.last_synced_at = now  

            except Exception as e:
                print(f"[Crypto Sync Error] {inv.investment_name}: {e}")
                continue

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"[Crypto Sync DB Error] {e}")
    finally:
        db.close()
        loop.close()


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
