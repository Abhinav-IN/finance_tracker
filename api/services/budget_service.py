from api.models.budget import Budget
from api.services.lookup_create_service import get_or_create_category
from api.schemas.budget import budgetRequest, budgetResponse, budgetQueryParam
from api.utils.budget import get_budget_status
from api.utils.budget_filter import apply_budget_filters, apply_pagination
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def create_budget_service(budget_request : budgetRequest, user_id: int, db : Session):
    curr_category_id = get_or_create_category(budget_request.category_name, user_id, db)
    new_budget = Budget(start_date = budget_request.start_date, end_date = budget_request.end_date, user_id = user_id, category_id = curr_category_id, amount = budget_request.amount)
    db.add(new_budget)
    try:
        db.commit()
        db.refresh(new_budget)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Multiple budget on this category")
    
    return {
        "id" : new_budget.id,
        "amount" : new_budget.amount,
        "start_date" : new_budget.start_date,
        "end_date" : new_budget.end_date,
        "category_id" : new_budget.category_id,
        "category_name" : new_budget.category.name
    }

def get_budget_service(budgetQuery : budgetQueryParam, user_id: int, db : Session):
    base_query = db.query(Budget).filter(Budget.user_id == user_id)
    base_query = apply_budget_filters(base_query, budgetQuery)
    base_query = apply_pagination(base_query, budgetQuery)
    budgets = base_query.all()

    response = []
    for b in budgets:
        response.append(budgetResponse(
            id=b.id,
            amount=b.amount,
            start_date=b.start_date,
            end_date=b.end_date,
            category_id=b.category_id,
            category_name=b.category.name 
        ))
    return response
    
def update_budget_service(budget_id : int, budget_request : budgetRequest, user_id: int, db : Session):
    budget_query = db.query(Budget).filter(Budget.user_id == user_id, Budget.id == budget_id)
    existing_budget = budget_query.first()

    if not existing_budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    curr_category_id = get_or_create_category(budget_request.category_name, user_id, db)
    
    budget_query = budget_query.update({
        "start_date" : budget_request.start_date,
        "end_date" : budget_request.end_date,
        "user_id" : user_id,
        "category_id" : curr_category_id,
        "amount" : budget_request.amount
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(existing_budget)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Multiple budget on this category")
    
    return {
        "id" : existing_budget.id,
        "amount" : existing_budget.amount,
        "start_date" : existing_budget.start_date,
        "end_date" : existing_budget.end_date,
        "category_id" : existing_budget.category_id,
        "category_name" : existing_budget.category.name
    }

def delete_budget_service(budget_id : int, user: dict, db : Session):
    budget = db.query(Budget).filter(Budget.id == budget_id).first()

    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if user["role"] != "admin" and budget.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own budget")
    
    db.delete(budget)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went erong in deleting budget")
    return 

def predict_budget_status(user_id: int, budget_id : int, db: Session):
    result = []
    status = get_budget_status(
            user_id=user_id,
            budget_id = budget_id,
            db=db
        )
    return result