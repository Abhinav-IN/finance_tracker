from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.dashboard import overviewResponse, expense_record, income_record
from api.services.dashboard_service import overview_of_user, get_past_30_day_expense, get_past_30_day_income
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Dashboard'], prefix='/api/v1/dashboard')

@router.get("/overview", status_code = status.HTTP_200_OK, response_model = overviewResponse)
def get_overview(user : dict = Depends(require_roles("user", "admin")),
                 db : Session = Depends(get_db)):
    return overview_of_user(user, db)

@router.get('/expense_record', status_code=status.HTTP_200_OK, response_model=List[expense_record])
def expense_record(user : dict = Depends(require_roles("user", "admin")),
                 db : Session = Depends(get_db)):
    return get_past_30_day_expense(user["id"], db)

@router.get('/income_record', status_code=status.HTTP_200_OK, response_model=List[income_record])
def income_record(user : dict = Depends(require_roles("user", "admin")),
                 db : Session = Depends(get_db)):
    return get_past_30_day_income(user["id"], db)