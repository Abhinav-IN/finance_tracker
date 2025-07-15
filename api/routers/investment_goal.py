from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.schemas.investment_goal import investment_goal_request, investment_goal_response, investmentGoalQueryParam, investment_goal_status_response 
from api.services.investment_goal_service import create_goal_service, get_goal_service, update_goal_service, delete_goal_service, get_all_investment_goal_status
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Investment_Goal'], prefix='/api/v1/investmentGoal')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=investment_goal_response)
def create_investment_goal(goalRequest : investment_goal_request,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return create_goal_service(goalRequest, user, db)

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[investment_goal_response])
def get_investment_goal(filter_query : investmentGoalQueryParam = Depends(),
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return get_goal_service(filter_query, user, db)

@router.put('/update/{goal_id}', status_code=status.HTTP_200_OK, response_model=investment_goal_response)
def update_investment_goal(goal_id : int,
                user_goal : investment_goal_request,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return update_goal_service(goal_id, user_goal, user, db)

@router.delete('/delete/{goal_id}', status_code=status.HTTP_200_OK)
def delete_investment_goal(goal_id : int,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    return delete_goal_service(goal_id, user, db)

@router.get("/status", response_model=List[investment_goal_status_response])
def get_all_goals_status(
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    return get_all_investment_goal_status(user=user, db=db)
