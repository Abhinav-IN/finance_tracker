from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.budget import Budget
from api.models.category import Category
from api.services.lookup_create_service import get_or_create_category
from api.schemas.budget import budgetRequest, budgetResponse, budgetQueryParam
from api.utils.budget import get_budget_status
from datetime import datetime
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

def create_budget_service(budget_request : budgetRequest,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    curr_category_id = get_or_create_category(budget_request.category_name, user['id'], db)
    new_budget = Budget(start_date = budget_request.start_date, end_date = budget_request.end_date, user_id = user['id'], category_id = curr_category_id, 
                        budget_amount = budget_request.budget_amount)
    db.add(new_budget)
    try:
        db.commit()
        db.refresh(new_budget)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Multiple budget on this category")
    
    return budgetResponse(
        budget_id=new_budget.budget_id,
        budget_amount=budget_request.budget_amount,
        start_date=budget_request.start_date,
        end_date=budget_request.end_date,
        category_id=curr_category_id,
        category_name=budget_request.category_name
    )

def get_budget_service(budgetQuery : budgetQueryParam = Depends(),
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    budgets_query = db.query(Budget).filter(Budget.user_id == user['id'])
    if budgetQuery.budget_id:
        budgets_query = budgets_query.filter(Budget.budget_id == budgetQuery.budget_id)
    if budgetQuery.start_date:
        budgets_query = budgets_query.filter(Budget.start_date == budgetQuery.start_date)
    if budgetQuery.end_date:
        budgets_query = budgets_query.filter(Budget.end_date == budgetQuery.end_date)
    if budgetQuery.category_name:
        budgets_query = budgets_query.join(Budget.category)
        budgets_query = budgets_query.filter(Category.category_name.ilike(f"%{budgetQuery.category_name}%"))
    if budgetQuery.greater_budget_amount:
        budgets_query = budgets_query.filter(Budget.budget_amount > budgetQuery.greater_budget_amount)
    if budgetQuery.lower_budget_amount:
        budgets_query = budgets_query.filter(Budget.budget_amount < budgetQuery.lower_budget_amount)
    if budgetQuery.exact_budget_amount:
        budgets_query = budgets_query.filter(Budget.budget_amount == budgetQuery.exact_budget_amount)
    
    budgets_query = budgets_query.offset(budgetQuery.get_offset).limit(budgetQuery.limit)
    budgets = budgets_query.all()

    response = []
    for b in budgets:
        response.append(budgetResponse(
            budget_id=b.budget_id,
            budget_amount=b.budget_amount,
            start_date=b.start_date,
            end_date=b.end_date,
            category_id=b.category_id,
            category_name=b.category.category_name 
        ))
    return response
    
def update_budget_service(budget_id : int,
                budget_request : budgetRequest,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):
    
    budget_query = db.query(Budget).filter(Budget.user_id == user['id'], Budget.budget_id == budget_id)
    existing_budget = budget_query.first()

    if not existing_budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    curr_category_id = get_or_create_category(budget_request.category_name, user['id'], db)
    
    budget_query = budget_query.update({
        "start_date" : budget_request.start_date,
        "end_date" : budget_request.end_date,
        "user_id" : user['id'],
        "category_id" : curr_category_id,
        "budget_amount" : budget_request.budget_amount
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(existing_budget)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Multiple budget on this category")
    
    return budgetResponse(
        budget_id=existing_budget.budget_id,
        budget_amount=existing_budget.budget_amount,
        start_date=existing_budget.start_date,
        end_date=existing_budget.end_date,
        category_id=curr_category_id,
        category_name=existing_budget.category.category_name
    )

def delete_budget_service(budget_id : int,
                user: dict = Depends(require_roles("user", "admin")), 
                db : Session = Depends(get_db)):

    budget = db.query(Budget).filter(Budget.budget_id == budget_id).first()

    if not budget:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    
    if user["role"] != "admin" and budget.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own budget")
    
    db.delete(budget)
    db.commit()
    return 

def get_all_budget_status(user_id: int, db: Session):
    today = datetime.now(ZoneInfo("Asia/Kolkata"))

    categories = db.query(Category).filter(Category.user_id == user_id).all()

    result = []

    for category in categories:
        status = get_budget_status(
            user_id=user_id,
            category_id=category.category_id,
            expense_date=today,
            db=db
        )
        if status:  
            result.append({
                "category_id": category.category_id,
                "category_name": category.category_name,
                **status
            })

    return result