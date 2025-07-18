from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.dashboard import overviewResponse
from api.services.dashboard_service import overview_of_user
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Dashboard'], prefix='/api/v1/dashboard')

@router.get("/overview", status_code = status.HTTP_200_OK, response_model = overviewResponse)
def get_overview(user : dict = Depends(require_roles("user", "admin")),
                 db : Session = Depends(get_db)):
    return overview_of_user(user, db)
    