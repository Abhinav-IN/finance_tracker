from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.utils.enums import UserRole
from api.schemas.investment import InvestmentCreateRequest, InvestmentUpdateRequest, InvestmentResponse, PaginatedInvestmentResponse, InvestmentQueryParams
from api.services.investment_service import create_investment_service, get_investment_service, update_investment_service,delete_investment_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Investment'], prefix='/api/v1/investment')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=InvestmentResponse)
def create_investment(  
    user_investment: InvestmentCreateRequest,  
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return create_investment_service(user_investment, user["id"], db)

@router.get('/', status_code=status.HTTP_200_OK, response_model=PaginatedInvestmentResponse)
def get_investment(
    filter_query: InvestmentQueryParams = Depends(),
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return get_investment_service(filter_query, user["id"], db)

@router.put('/update/{investment_id}', status_code=status.HTTP_200_OK, response_model=InvestmentResponse)
def update_investment(
    investment_id: int,
    user_investment: InvestmentUpdateRequest,  
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return update_investment_service(investment_id, user_investment, user["id"], db)

@router.delete('/delete/{investment_id}', status_code=status.HTTP_200_OK)
def delete_investment(
    investment_id: int,
    user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
    db: Session = Depends(get_db),
):
    return delete_investment_service(investment_id, user["id"], db)
