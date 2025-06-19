from celery import Celery
from api.config import settings
from api.utils import send_email

celery_app = Celery(
    "worker",
    broker=f"redis://{settings.redis_hostname}:{settings.redis_port}/{settings.redis_db}"                                         
)

@celery_app.task
def send_password_reset_email(to_email : str, reset_link : str):
    send_email(
        subject="Reset your password",
        to=to_email,
        body=f"Click here to reset your password: {reset_link}"
    )
