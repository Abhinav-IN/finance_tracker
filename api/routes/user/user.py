from fastapi import APIRouter, status, HTTPException, Response
from api import schemas, models, utils
from sqlalchemy.orm import Session
from fastapi import Depends
from api.database import get_db
from typing import List

router = APIRouter()

@router.post("/createProfile", status_code = status.HTTP_201_CREATED, response_model=schemas.Profile)
def create_profile(new_profile : schemas.createProfile, db : Session = Depends(get_db)):
    new_profile.password = utils.hashing_password(new_profile.password)

    newProfile = models.User(**new_profile.model_dump())
    db.add(newProfile)
    db.commit()
    db.refresh(newProfile)
    return newProfile

@router.get("/profile/{id}", response_model=schemas.Profile)
def get_profile(id : int, db : Session = Depends(get_db)):
    reqProfile = db.query(models.User).filter(models.User.id == id).first()
    if not reqProfile:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f"Profile with id {id} does not exist")
    
    return reqProfile

@router.put("/updateProfile/{id}", response_model=schemas.Profile)
def update_profile (new_profile : schemas.createProfile, id : int, db : Session = Depends(get_db)):
    profile_query = db.query(models.User).filter(models.User.id == id)
    existing_profile = profile_query.first()
    
    new_profile.password = utils.hashing_password(new_profile.password)

    if not existing_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Profile with {id} does not exist")
    
    profile_query.update(new_profile.model_dump(), synchronize_session=False)  
    db.commit()
    return profile_query.first()

@router.delete("/deleteProfile/{id}")
def delete_profile(id : int, db : Session = Depends(get_db)):
    profile_query = db.query(models.User).filter(models.User.id == id)
    existing_profile = profile_query.first()
    if not existing_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Profile with {id} does not exist")
    
    profile_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    
