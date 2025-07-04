from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.category import Category
from api.models.user import User
from api.schemas.category import categoryCreate
from api.utils.validator import user_active
from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def create_category_service(category : categoryCreate, 
                    user: dict = Depends(require_roles("user", "admin", "moderator")), 
                    db : Session = Depends(get_db)):
    user_active(user, db)
    category_name = category.category_name.strip().lower()
    new_category = Category(category_name = category_name,  user_id=user["id"])
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exist")

    return {
        "category_id" : new_category.category_id,
        "category_name" : new_category.category_name
    }

def get_categories_service(
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    user_active(user, db)
    categories = db.query(Category).filter(Category.user_id == user["id"]).all()
    return categories

def get_category_by_id_service(
    category_id: int,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    user_active(user, db)
    category = db.query(Category).filter(Category.category_id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if user["role"] != "admin" and category.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="You can only access your own category")

    return category

def update_category_service(
    category_id: int,
    category_update: categoryCreate,
    user: dict = Depends(require_roles("user", "admin", "moderator")),
    db: Session = Depends(get_db)
):
    user_active(user, db)

    category_query = db.query(Category).filter(
        Category.category_id == category_id,
        Category.user_id == user['id']
    )
    existing_category = category_query.first()

    if existing_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")

    category_name = category_update.category_name.strip().lower()
    try:
        category_query.update({"category_name": category_name}, synchronize_session=False)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exist"
        )

    return category_query.first()

def delete_category_service(
    category_id: int,
    user: dict = Depends(require_roles("user", "admin")),  
    db: Session = Depends(get_db)
):
    user_active(user, db)
    category = db.query(Category).filter(Category.category_id == category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if user["role"] != "admin" and category.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own category")

    if category.transactions or category.budgets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category is linked to other data and cannot be deleted")

    db.delete(category)
    db.commit()
    return
