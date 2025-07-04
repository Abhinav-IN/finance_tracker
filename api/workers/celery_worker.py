from api.core.config import settings
from api.services.email_service import send_password_reset_email_service, send_verification_email_service
from celery import Celery


celery_app = Celery(
    "worker",
    broker=f"redis://{settings.redis_hostname}:{settings.redis_port}/{settings.redis_db}"                                         
)

@celery_app.task
def password_reset_email(to_email : str, reset_link : str):
    send_password_reset_email_service(to_email, reset_link)
    
@celery_app.task
def verification_email(to_email: str, verification_link: str):
    send_verification_email_service(to_email, verification_link)

