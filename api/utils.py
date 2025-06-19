from passlib.context import CryptContext
from . import models
from fastapi import Request
import smtplib
from email.message import EmailMessage
from api.config import settings
import re

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashing_password(password: str):
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def authenticate_user(user_credentials, db):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.password):
        return False
    return user
    
def get_client_ip(request: Request):
    x_forwarded_for = request.headers.get("X-Forwarded-For")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.client.host
    return ip

def send_email(subject: str, to: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)

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