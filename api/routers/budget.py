from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.budget import budgetRequest, budgetResponse, budgetQueryParam
from api.services.budget_service import create_budget_service, get_budget_service, update_budget_service, delete_budget_service
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Budget'], prefix='/api/v1/budget')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=budgetResponse)
def create_budget(budget_request : budgetRequest,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return create_budget_service(budget_request, user, db)

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[budgetResponse])
def get_budget(budgetQuery : budgetQueryParam = Depends(),
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return get_budget_service(budgetQuery, user, db)

@router.put('/update/{budget_id}', status_code=status.HTTP_200_OK, response_model=budgetResponse)
def update_budget(budget_id : int,
                budget_request : budgetRequest,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return update_budget_service(budget_id, budget_request, user, db)

@router.delete('/delete/{budget_id}', status_code=status.HTTP_200_OK)
def delete_budget(budget_id : int,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return delete_budget_service(budget_id, user, db)