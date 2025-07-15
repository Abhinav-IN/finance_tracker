from api.tasks.celery_worker import celery_app
from api.services.email_service import (
    send_password_reset_email_service,
    send_verification_email_service,
    reminder_subscription_email_service,
    subscription_email_service
)

@celery_app.task
def password_reset_email(to_email: str, reset_link: str):
    send_password_reset_email_service(to_email, reset_link)

@celery_app.task
def verification_email(to_email: str, verification_link: str):
    send_verification_email_service(to_email, verification_link)

@celery_app.task
def reminder_subscription_email(to_email: str, subscription_name: str, amount: int):
    reminder_subscription_email_service(to_email, subscription_name, amount)

@celery_app.task
def subscription_email(to_email: str, subscription_name: str, amount: int):
    subscription_email_service(to_email, subscription_name, amount)
