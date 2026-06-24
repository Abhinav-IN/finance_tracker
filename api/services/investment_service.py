from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.models.investment import Investment
from api.schemas.investment import InvestmentCreateRequest, InvestmentUpdateRequest, InvestmentResponse, PaginatedInvestmentResponse, InvestmentQueryParams
from api.utils.time import ist_now, IST
from datetime import timedelta, datetime, time
from sqlalchemy import func, or_, desc, cast, String


def _investment_to_response(inv: Investment) -> InvestmentResponse:
    """Build API response from ORM row (avoids model_validate quirks with SQLAlchemy internals)."""
    latest_price = inv.prices[0].price_per_unit if inv.prices else None
    current_value = (
        latest_price * inv.units
        if latest_price and inv.units
        else inv.amount
    )
    pnl = current_value - inv.amount if current_value is not None else None
    return InvestmentResponse(
        id=inv.id,
        name=inv.name,
        investment_type=inv.investment_type,
        platform=inv.platform,
        amount=inv.amount,
        units=inv.units,
        buy_price=inv.buy_price,
        date=inv.date,
        description=inv.description,
        status=inv.status,
        created_at=inv.created_at,
        updated_at=inv.updated_at,
        current_price=latest_price,
        current_value=current_value,
        pnl=pnl,
    )


def create_investment_service(new_investment: InvestmentCreateRequest, user_id: int , db: Session):
    investment = Investment(
        user_id=user_id,
        name=new_investment.name,
        investment_type=new_investment.investment_type,
        platform=new_investment.platform,
        amount=new_investment.amount,
        units=new_investment.units,
        buy_price=new_investment.buy_price,
        date=new_investment.date,
        description = new_investment.description,
        status=new_investment.status,
    )

    db.add(investment)
    try:
        db.commit()
        db.refresh(investment)
    except Exception as e:
        db.rollback()
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creating investment")

    return _investment_to_response(investment)

def get_investment_service(params: InvestmentQueryParams, user_id: int, db: Session):
    query = db.query(Investment).filter(Investment.user_id == user_id)

    if params.id is not None:
        query = query.filter(Investment.id == params.id)
    if params.status is not None:
        query = query.filter(Investment.status == params.status)
    if params.min_amount is not None:
        query = query.filter(Investment.amount >= params.min_amount)
    if params.max_amount is not None:
        query = query.filter(Investment.amount <= params.max_amount)
    if params.amount is not None:
        query = query.filter(Investment.amount == params.amount)
    if params.date is not None:
        start = datetime.combine(params.date, time.min).replace(tzinfo=IST)
        end = datetime.combine(params.date, time.max).replace(tzinfo=IST)
        query = query.filter(Investment.date.between(start, end))
    if params.search is not None:
        search_text = params.search.strip()
        # Avoid .ilike() on native ENUM (MySQL); cast to string for substring match.
        type_as_str = cast(Investment.investment_type, String)
        query = query.filter(
            or_(
                Investment.name.ilike(f"%{search_text}%"),
                Investment.description.ilike(f"%{search_text}%"),
                type_as_str.like(f"%{search_text}%"),
                Investment.platform.ilike(f"%{search_text}%"),
            )
        )

    total = query.count()
    investments = (
        query.order_by(desc(Investment.date), desc(Investment.id))
        .offset(params.offset)
        .limit(params.limit)
        .all()
    )

    responses = [_investment_to_response(inv) for inv in investments]

    return PaginatedInvestmentResponse(
        total=total,
        page=params.page,
        limit=params.limit,
        data=responses,
    )

def update_investment_service(investment_id: int, data: InvestmentUpdateRequest, user_id: int, db: Session):
    investment = (
        db.query(Investment)
        .filter(Investment.id == investment_id, Investment.user_id == user_id)
        .first()
    )

    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(investment, field, value)

    try:
        db.commit()
        db.refresh(investment)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in updating investment")

    return _investment_to_response(investment)

def delete_investment_service(investment_id: int, user_id: int, db: Session,):
    investment = (
        db.query(Investment)
        .filter(Investment.id == investment_id, Investment.user_id == user_id)
        .first()
    )

    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    db.delete(investment)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Somethign went wrong in deleting investment")

    return

def investment_overview_service(user: dict, db: Session):
    thirty_days_ago = ist_now() - timedelta(days=30)
    total_investment = db.query(Investment).filter(
        Investment.user_id == user["id"],
        Investment.date >= thirty_days_ago
    ).with_entities(func.sum(Investment.amount)).scalar() or 0

    seven_days_ago = ist_now() - timedelta(days=7)
    total_investment_7_days = db.query(Investment).filter(
        Investment.user_id == user["id"],
        Investment.date >= seven_days_ago
    ).with_entities(func.sum(Investment.amount)).scalar() or 0

    current_month_start = ist_now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    total_investment_current_month = db.query(Investment).filter(
        Investment.user_id == user["id"],
        Investment.date >= current_month_start
    ).with_entities(func.sum(Investment.amount)).scalar() or 0
    average_monthly_investment = total_investment_current_month / ((ist_now()).day or 1)

    current_week_start = ist_now() - timedelta(days=ist_now().weekday())
    total_investment_current_week = db.query(Investment).filter(
        Investment.user_id == user["id"],
        Investment.date >= current_week_start
    ).with_entities(func.sum(Investment.amount)).scalar() or 0
    average_weekly_investment = total_investment_current_week / ((ist_now()).weekday() + 1 or 1)
    
    return {
        "total_investment_last_30_days": total_investment,
        "total_investment_last_7_days": total_investment_7_days,
        "total_investment_current_month": total_investment_current_month,
        "average_monthly_investment": average_monthly_investment,
        "average_weekly_investment": average_weekly_investment
    }