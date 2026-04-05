from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from api.database.session import get_db
from api.core.oauth2 import require_roles
from api.utils.enums import UserRole
from api.schemas.investment_price import InvestmentPriceCreate, InvestmentPriceResponse
from api.services.investment_price_service import  create_investment_price_service, get_investment_price_history_service

router = APIRouter(prefix="/api/v1/investment_prices", tags=["Investment Prices"])

@router.post("/create",response_model=InvestmentPriceResponse)
def create_price(
    data: InvestmentPriceCreate,
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return create_investment_price_service(data, user["id"], db)


@router.get("/{investment_id}", response_model=list[InvestmentPriceResponse])
def get_price_history(
    investment_id: int,
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
    db: Session = Depends(get_db)
):
    return get_investment_price_history_service(investment_id, user["id"], db)
