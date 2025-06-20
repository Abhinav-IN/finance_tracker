from fastapi import APIRouter, status, Depends, HTTPException
from .. import schemas, oauth2, models, database
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(tags=['Categories'], prefix='/category')

@router.post('/create', status_code=status.HTTP_201_CREATED, response_model=schemas.categoryResponse)
def create_category(category : schemas.categoryCreate, 
                    user_id : int = Depends(oauth2.get_current_user), 
                    db : Session = Depends(database.get_db)):
    category_name = category.category_name
    new_category = models.Category(category_name = category_name, user_id = user_id)
    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return {
        "category_id" : new_category.category_id,
        "category_name" : new_category.category_name
    }

@router.get('/', status_code=status.HTTP_200_OK, response_model=List[schemas.categoryResponse])
def get_category(user_id : int = Depends(oauth2.get_current_user), 
                db : Session = Depends(database.get_db) ):
    category = db.query(models.Category).filter(models.Category.user_id == user_id).all()
    return category

@router.get('/{category_id}', status_code=status.HTTP_200_OK, response_model=schemas.categoryResponse)
def get_category_perId(category_id : int,
                    user_id : int = Depends(oauth2.get_current_user), 
                    db : Session = Depends(database.get_db)):
    category = db.query(models.Category).filter(models.Category.category_id == category_id,
                                                models.Category.user_id == user_id).first()
    return category

@router.put('/{category_id}', status_code=status.HTTP_200_OK, response_model=schemas.categoryResponse)
def update_category(category_id : int,
                    category_update : schemas.categoryCreate,
                    user_id : int = Depends(oauth2.get_current_user), 
                    db : Session = Depends(database.get_db)):
    category_query = db.query(models.Category).filter(models.Category.category_id == category_id,
                                                      models.Category.user_id == user_id)
    existing_category = category_query.first()
    if existing_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category did not exist")
    category_query.update(category_update.model_dump(), synchronize_session=False)
    db.commit()

    return category_query.first()

@router.delete('/delete{category_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id : int,
                    user_id : int = Depends(oauth2.get_current_user), 
                    db : Session = Depends(database.get_db)):
    category_query = db.query(models.Category).filter(models.Category.category_id == category_id,
                                                      models.Category.user_id == user_id)
    curr_category = category_query.first()

    if curr_category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category did not exist")
    
    category_query.delete(synchronize_session=False)
    db.commit()
    return
