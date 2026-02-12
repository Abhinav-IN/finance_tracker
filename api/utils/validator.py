import re
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

def validate_date_and_amount(self : Self):
    if self.start_date >= self.end_date:
        raise ValueError("Minimum duration of budget should be one day")
    if self.amount <= 0:
        raise ValueError("Budget amount must be greater then zero")
    return self

