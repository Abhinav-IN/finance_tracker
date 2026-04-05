from api.tasks.subscription import process_subscription_billing
from api.tasks.celery_worker import celery_app


@celery_app.task(name="api.tasks.scheduler_service.run_subscription_job")
def run_subscription_job():
    process_subscription_billing()