from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.dashboard import overviewResponse, transaction_record
from api.services.dashboard_service import overview_of_user, get_past_30_day_transaction
from api.utils.enums import TransactionDirection
from api.utils.enums import UserRole
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Dashboard'], prefix='/api/v1/dashboard')

@router.get("/overview", status_code = status.HTTP_200_OK, response_model = overviewResponse)
def get_overview(user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),
                 db : Session = Depends(get_db)):
    return overview_of_user(user["id"], db)

@router.get('/transaction_record/{direction}', status_code=status.HTTP_200_OK, response_model=List[transaction_record])
def transaction_record(direction : TransactionDirection, user : dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return get_past_30_day_transaction(user["id"], direction, db)