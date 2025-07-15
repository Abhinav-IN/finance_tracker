from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.investment_goal import InvestmentGoal
from api.schemas.investment_goal import investment_goal_request, investment_goal_response, investmentGoalQueryParam, investment_goal_status_response
from api.utils.investment import link_investments_to_goal
from datetime import datetime, time
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from zoneinfo import ZoneInfo

def create_goal_service(goalRequest : investment_goal_request,
                           user : dict = Depends(require_roles("user", "admin")),
                           db : Session = Depends(get_db)):
    new_goal = InvestmentGoal(
        goal_name = goalRequest.goal_name,
        description = goalRequest.description,
        start_date = goalRequest.start_date,
        end_date = goalRequest.end_date,
        user_id = user["id"],
        goal_amount = goalRequest.goal_amount,
        applies_to_all_investments = goalRequest.applies_to_all_investments
    )
    db.add(new_goal)
    try:
        db.commit()
        db.refresh(new_goal)
    except Exception as e:
        print(e)
        db.rollback()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Something went wrong while adding investment goal")
    
    link_investments_to_goal(new_goal.goal_id, goalRequest.investment_ids, user["id"], db)
    investments = new_goal.investments

    current_value = sum(investment.current_value or 0 for investment in investments)
    new_goal.current_value = current_value
    db.commit()
    db.refresh(new_goal)

    return investment_goal_response(
        goal_id = new_goal.goal_id,
        goal_name = new_goal.goal_name,
        goal_amount = new_goal.goal_amount,
        current_value = new_goal.current_value,
        start_date = new_goal.start_date,
        end_date = new_goal.end_date,
        applies_to_all_investments = new_goal.applies_to_all_investments,
        investment_ids = [inv.investment_id for inv in investments],
        description = new_goal.description
    )

def get_goal_service(
    filter_query: investmentGoalQueryParam,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
) -> List[investment_goal_response]:

    ist = ZoneInfo("Asia/Kolkata")
    curr_query = (
        db.query(InvestmentGoal)
        .filter(InvestmentGoal.user_id == user["id"])
        .options(joinedload(InvestmentGoal.investments))  # eager loading
    )

    if filter_query.goal_id:
        curr_query = curr_query.filter(InvestmentGoal.goal_id == filter_query.goal_id)

    if filter_query.goal_name:
        curr_query = curr_query.filter(
            InvestmentGoal.goal_name.ilike(filter_query.goal_name.strip())
        )

    if filter_query.exact_amount:
        curr_query = curr_query.filter(
            InvestmentGoal.goal_amount == filter_query.exact_amount
        )

    if filter_query.greater_amount:
        curr_query = curr_query.filter(
            InvestmentGoal.goal_amount > filter_query.greater_amount
        )

    if filter_query.lower_amount:
        curr_query = curr_query.filter(
            InvestmentGoal.goal_amount < filter_query.lower_amount
        )

    if filter_query.start_date:
        start_of_day = datetime.combine(filter_query.start_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.start_date, time.max).replace(tzinfo=ist)
        curr_query = curr_query.filter(InvestmentGoal.start_date.between(start_of_day, end_of_day))

    if filter_query.end_date:
        start_of_day = datetime.combine(filter_query.end_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.end_date, time.max).replace(tzinfo=ist)
        curr_query = curr_query.filter(InvestmentGoal.end_date.between(start_of_day, end_of_day))

    if filter_query.search:
        curr_query = curr_query.filter(
            InvestmentGoal.description.ilike(f"%{filter_query.search}%")
        )

    curr_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit)
    goals = curr_query.all()

    response = []
    for g in goals:
        investments = g.investments
        response.append(investment_goal_response(
            goal_id=g.goal_id,
            goal_name=g.goal_name,
            goal_amount=g.goal_amount,
            current_value=g.current_value,
            start_date=g.start_date,
            end_date=g.end_date,
            applies_to_all_investments=g.applies_to_all_investments,
            investment_ids=[inv.investment_id for inv in investments],
            description=g.description
        ))

    return response
def update_goal_service(goal_id : int,
                        user_goal : investment_goal_request,
                        user : dict = Depends(require_roles("admin", "user")),
                        db : Session = Depends(get_db)):
    curr_goal_query = db.query(InvestmentGoal).filter(InvestmentGoal.goal_id == goal_id, InvestmentGoal.user_id == user["id"])
    curr_goal = curr_goal_query.first()

    if not curr_goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal Not Found")
    
    link_investments_to_goal(curr_goal.goal_id, user_goal.investment_ids, user["id"], db)
    investments = curr_goal.investments

    curr_goal_query = curr_goal_query.update({
        "goal_name" : user_goal.goal_name,
        "description" : user_goal.description,
        "start_date" : user_goal.start_date,
        "end_date" : user_goal.end_date,
        "goal_amount" : user_goal.goal_amount,
        "applies_to_all_investments" : user_goal.applies_to_all_investments
        },synchronize_session=False)

    try:
        db.commit()
        db.refresh(curr_goal)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating goal")
    
    current_value = sum(investment.current_value or 0 for investment in investments)
    curr_goal.current_value = current_value
    db.commit()
    db.refresh(curr_goal)

    return investment_goal_response(
        goal_id = curr_goal.goal_id,
        goal_name = curr_goal.goal_name,
        goal_amount = curr_goal.goal_amount,
        current_value = curr_goal.current_value,
        start_date = curr_goal.start_date,
        end_date = curr_goal.end_date,
        applies_to_all_investments = curr_goal.applies_to_all_investments,
        investment_ids = [inv.investment_id for inv in investments],
        description = curr_goal.description
    )

def delete_goal_service(goal_id : int,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):

    goal = db.query(InvestmentGoal).filter(InvestmentGoal.goal_id == goal_id).first()

    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    if user["role"] != "admin" and goal.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own goal")
    
    db.delete(goal)
    db.commit()
    return 

def get_all_investment_goal_status(
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    goals = db.query(InvestmentGoal).filter(InvestmentGoal.user_id == user["id"]).all()
    response = []

    now = datetime.now().date()

    for goal in goals:
        current_value = goal.current_value or 0
        remaining = round(goal.goal_amount - current_value, 2)
        is_completed = current_value >= goal.goal_amount
        deadline_passed = now > goal.end_date.date()

        # Set status
        if is_completed:
            status = "completed"
        elif deadline_passed:
            status = "expired"
        else:
            status = "active"

        # Optional message
        message = None
        if status == "completed":
            message = f"Goal '{goal.goal_name}' completed!"
        elif status == "expired":
            message = f"Goal '{goal.goal_name}' deadline has passed!"
        elif remaining <= 0.1 * goal.goal_amount:
            message = f"Only ₹{remaining} left to complete '{goal.goal_name}'"

        response.append(investment_goal_status_response(
            goal_id=goal.goal_id,
            goal_name=goal.goal_name,
            goal_amount=goal.goal_amount,
            current_value=current_value,
            remaining=remaining,
            start_date=goal.start_date,
            end_date=goal.end_date,
            status=status,
            message=message
        ))

    return response

