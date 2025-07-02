from fastapi import APIRouter, status, Depends, HTTPException
from .. import schemas, oauth2, models, database
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Categories'], prefix='/api/v1/category')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.categoryResponse)
def create_category(category : schemas.categoryCreate, 
                    user: dict = Depends(oauth2.require_roles("user", "admin", "moderator")), 
                    db : Session = Depends(database.get_db)):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    
    category_name = category.category_name.strip().lower()
    new_category = models.Category(category_name = category_name,  user_id=user["id"])
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {
        "category_id" : new_category.category_id,
        "category_name" : new_category.category_name
    }

@router.get('/', response_model=List[schemas.categoryResponse])
def get_categories(
    user: dict = Depends(oauth2.require_roles("user", "admin")),
    db: Session = Depends(database.get_db)
):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    categories = db.query(models.Category).filter(models.Category.user_id == user["id"]).all()
    return categories


@router.get('/{category_id}', response_model=schemas.categoryResponse)
def get_category_by_id(
    category_id: int,
    user: dict = Depends(oauth2.require_roles("user", "admin")),
    db: Session = Depends(database.get_db)
):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    category = db.query(models.Category).filter(models.Category.category_id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if user["role"] != "admin" and category.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="You can only access your own category")

    return category


@router.put('/{category_id}', status_code=status.HTTP_200_OK, response_model=schemas.categoryResponse)
def update_category(category_id : int,
                    category_update : schemas.categoryCreate,
                    user: dict = Depends(oauth2.require_roles("user", "admin", "moderator")), 
                    db : Session = Depends(database.get_db)):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    category_query = db.query(models.Category).filter(models.Category.category_id == category_id,
                    models.Category.user_id == user['id'])
    existing_category = category_query.first()
    if existing_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category did not exist")
    category_query.update(category_update.model_dump(), synchronize_session=False)

    data_to_update = category_update.model_dump()
    if "name" in data_to_update and data_to_update["name"]:
        data_to_update["name"] = data_to_update["name"].strip().lower()
        
    db.commit()

    return category_query.first()

@router.delete('/delete/{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    user: dict = Depends(oauth2.require_roles("user", "admin")),  
    db: Session = Depends(database.get_db)
):
    if user["is_active"] == False:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is not verified")
    category = db.query(models.Category).filter(models.Category.category_id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if user["role"] != "admin" and category.user_id != user["id"]:
        raise HTTPException(status_code=403, detail="You can only delete your own category")

    if category.transactions or category.budgets:
        raise HTTPException(status_code=400, detail="Category is linked to other data and cannot be deleted")

    db.delete(category)
    db.commit()
    return

