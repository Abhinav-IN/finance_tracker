from api.core.config import settings
from celery import Celery
from api.workers import celery_config  

celery_app = Celery(
    "worker",
    broker=f"redis://{settings.redis_hostname}:{settings.redis_port}/{settings.redis_db}"
)

celery_app.config_from_object(celery_config)  

celery_app.conf.beat_schedule = celery_config.beat_schedule
celery_app.conf.timezone = celery_config.timezone
celery_app.conf.beat_schedule_filename = celery_config.beat_schedule_filename  

celery_app.autodiscover_tasks(["api.tasks", "api.utils"])
