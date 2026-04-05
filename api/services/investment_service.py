from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.models.investment import Investment
from api.schemas.investment import InvestmentCreateRequest, InvestmentUpdateRequest, InvestmentResponse, PaginatedInvestmentResponse, InvestmentQueryParams

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
        maturity_date=new_investment.maturity_date,
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

    return InvestmentResponse.model_validate(investment)

def get_investment_service(params: InvestmentQueryParams, user_id: int, db: Session):
    query = db.query(Investment).filter(Investment.user_id == user_id)

    if params.investment_type:
        query = query.filter(Investment.investment_type == params.investment_type)
    if params.platform:
        query = query.filter(Investment.platform.ilike(f"%{params.platform}%"))
    if params.status:
        query = query.filter(Investment.status == params.status)
    if params.min_amount:
        query = query.filter(Investment.amount >= params.min_amount)
    if params.max_amount:
        query = query.filter(Investment.amount <= params.max_amount)

    total = query.count()
    investments = query.offset(params.offset).limit(params.limit).all()

    responses = []
    for inv in investments:
        latest_price = inv.prices[0].price_per_unit if inv.prices else None
        current_value = (
            latest_price * inv.units
            if latest_price and inv.units
            else inv.amount
        )
        pnl = current_value - inv.amount if current_value else None

        responses.append(
            InvestmentResponse(
                **inv.__dict__,
                current_price=latest_price,
                current_value=current_value,
                pnl=pnl,
                
            )
        )

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

    return InvestmentResponse.model_validate(investment)

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
