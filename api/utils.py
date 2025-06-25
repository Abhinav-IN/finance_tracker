from passlib.context import CryptContext
from . import models
import smtplib
from email.message import EmailMessage
from api.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashing_password(password: str):
    return pwd_context.hash(password)

def verify_password(password, hashed_password):
    return pwd_context.verify(password, hashed_password)

def authenticate_user(user_credentials, db):
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        return False
    return user
    

def send_email(subject: str, to: str, body: str):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg.set_content(body)

    with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port) as server:
        server.login(settings.smtp_user, settings.smtp_pass)
        server.send_message(msg)

