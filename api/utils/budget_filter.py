from sqlalchemy.orm import Query
from api.models.budget import Budget
from api.models.category import Category
from api.schemas.budget import budgetQueryParam


def apply_budget_filters(query: Query, params: budgetQueryParam):
    if params.id:
        query = query.filter(Budget.id == params.id)

    if params.start_date:
        query = query.filter(Budget.start_date == params.start_date)

    if params.end_date:
        query = query.filter(Budget.end_date == params.end_date)

    if params.category_name:
        query = query.join(Budget.category).filter(
            Category.name.ilike(f"%{params.category_name}%")
        )

    if params.greater_budget_amount:
        query = query.filter(Budget.amount > params.greater_budget_amount)

    if params.lower_budget_amount:
        query = query.filter(Budget.amount < params.lower_budget_amount)

    if params.exact_budget_amount:
        query = query.filter(Budget.amount == params.exact_budget_amount)

    return query

def apply_pagination(query: Query, params: budgetQueryParam):
    return query.offset(params.get_offset).limit(params.limit)