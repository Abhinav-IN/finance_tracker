from api.models.category import Category
from api.schemas.category import categoryCreate
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def create_category_service(category : categoryCreate, user_id: int, db : Session):
    category_name = category.name.strip().lower()
    new_category = Category(name = category_name,  user_id = user_id)
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exist")

    return {
        "id" : new_category.id,
        "name" : new_category.name
    }

def get_categories_service(user_id: int, db: Session):
    categories = db.query(Category).filter(Category.user_id == user_id).all()
    return categories

def get_category_by_id_service(category_id: int, user: dict, db: Session):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if user["role"] != "admin" and category.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only access your own category")

    return category

def update_category_service(category_id: int, category_update: categoryCreate, user_id: int, db: Session ):
    category_query = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == user_id
    )
    existing_category = category_query.first()

    if existing_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist")

    category_name = category_update.name.strip().lower()
    try:
        category_query.update({"name": category_name}, synchronize_session=False)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exist")

    return category_query.first()

def delete_category_service(category_id: int, user: dict, db: Session ):
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if user["role"] != "admin" and category.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own category")

    if category.transactions or category.budgets:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category is linked to other data and cannot be deleted")

    db.delete(category)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be deleted")
    return
