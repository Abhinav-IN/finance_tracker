from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.subscription import SubscriptionCreate, SubscriptionResponse, SubscriptionQueryParam, SubscriptionOverview, PaginatedSubscriptionResponse
from api.services.subscription_service import create_subscription_service, get_subscription_service, update_subscription_service, delete_subscription_service, overview_services
from api.utils.enums import UserRole
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

router = APIRouter(tags=['Subscription'], prefix='/api/v1/subscription')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=SubscriptionResponse)
def create_subscription(subscription_request : SubscriptionCreate, user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return create_subscription_service(subscription_request, user["id"], db)

@router.get('/', status_code=status.HTTP_200_OK, response_model=PaginatedSubscriptionResponse)
def get_subscription(subscriptionQuery : SubscriptionQueryParam = Depends(), user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return get_subscription_service(subscriptionQuery, user["id"], db)

@router.put('/update/{subscription_id}', status_code=status.HTTP_200_OK, response_model=SubscriptionResponse)
def update_subscription(subscription_id : int, subscription_request : SubscriptionCreate, user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return update_subscription_service(subscription_id, subscription_request, user["id"], db)

@router.delete('/delete/{subscription_id}', status_code=status.HTTP_200_OK)
def delete_subscription(subscription_id : int, user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)), db : Session = Depends(get_db)):
    return delete_subscription_service(subscription_id, user, db)

@router.get('/overview', status_code=status.HTTP_200_OK, response_model=SubscriptionOverview)
def overview_income(user: dict = Depends(require_roles(UserRole.USER, UserRole.ADMIN)),  db: Session = Depends(get_db)):
    return overview_services(user["id"], db)