from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.category import categoryCreate, categoryResponse
from api.services.category_service import create_category_service, get_categories_service, get_category_by_id_service, update_category_service, delete_category_service
from fastapi import APIRouter, Depends, status
from typing import List
from sqlalchemy.orm import Session

router = APIRouter(tags=['Categories'], prefix='/api/v1/category')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=categoryResponse)
def create_category(category : categoryCreate, 
                    user: dict = Depends(require_roles("user", "admin", "moderator")), 
                    db : Session = Depends(get_db)):
    return create_category_service(category, user, db)
    
@router.get('/', response_model=List[categoryResponse])
def get_categories(
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    return get_categories_service(user, db)

@router.get('/{category_id}', response_model=categoryResponse)
def get_category_by_id(
    category_id: int,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    return get_category_by_id_service(category_id, user, db)

@router.put('/{category_id}', status_code=status.HTTP_200_OK, response_model=categoryResponse)
def update_category(category_id : int,
                    category_update : categoryCreate,
                    user: dict = Depends(require_roles("user", "admin", "moderator")), 
                    db : Session = Depends(get_db)):
    return update_category_service(category_id, category_update, user, db)

@router.delete('/delete/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    user: dict = Depends(require_roles("user", "admin")),  
    db: Session = Depends(get_db)
):
    return delete_category_service(category_id, user, db)