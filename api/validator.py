import re

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