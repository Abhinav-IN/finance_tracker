from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.investment import InvestmentRequest, investmentResponse, InvestmentQueryParam  # ✅ FIXED
from api.services.investment_service import (
    create_investment_service,
    get_investment_service,
    update_investment_service,
    delete_investment_service,
)
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Investment'], prefix='/api/v1/investment')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=investmentResponse)
async def create_investment(  # ✅ typo fixed in function name
    user_investment: InvestmentRequest,  # ✅ FIXED
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return await create_investment_service(user_investment, user, db)

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[investmentResponse])
def get_investment(
    filter_query: InvestmentQueryParam = Depends(),
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return get_investment_service(filter_query, user, db)

@router.put('/update/{investment_id}', status_code=status.HTTP_200_OK, response_model=investmentResponse)
async def update_investment(
    investment_id: int,
    user_investment: InvestmentRequest,  # ✅ FIXED
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return await update_investment_service(investment_id, user_investment, user, db)

@router.delete('/delete/{investment_id}', status_code=status.HTTP_200_OK)
def delete_investment(
    investment_id: int,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db),
):
    return delete_investment_service(investment_id, user, db)
