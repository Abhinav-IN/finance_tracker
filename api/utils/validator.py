from api.models.user import User
from fastapi import HTTPException, status
import re
from sqlalchemy.orm import Session
from typing import Self

def validate_password_strength(password: str) -> str:
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase character")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase character")
    if not re.search(r"\d", password):
        raise ValueError("Password must contain at least one digit")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise ValueError("Password must contain at least one special character")
    return password

def gender_check(gender: str) -> str:
    allowed = {"male", "female", "other"}
    if gender.lower() not in allowed:
        raise ValueError(f"Gender must be one of {allowed}")
    return gender.lower()

def user_active(user : dict, db : Session):
    is_active = db.query(User.is_active).filter(User.id == user["id"]).scalar()
    if not is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not verified")

def validate_date_and_amount(self : Self):
    if self.start_date >= self.end_date:
        raise ValueError("Minimum duration of budget should be one day")
    if self.budget_amount <= 0:
        raise ValueError("Budget amount must be greater then zero")
    return self

def validate_amount(model):
    value = getattr(model, "amount", None) or getattr(model, "price", None)
    if value is None:
        raise ValueError("Amount or price field is required.")
    if value <= 0:
        raise ValueError("Amount must be greater than 0")
    return model
