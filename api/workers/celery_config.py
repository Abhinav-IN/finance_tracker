from celery.schedules import crontab

beat_schedule = {
    "run-daily-subscription-job": {
        "task": "api.tasks.scheduler_service.run_subscription_job",
        "schedule": crontab(hour=18, minute=31),
    },
}

timezone = "Asia/Kolkata"
beat_schedule_filename = "/app/celery-beat/celerybeat-schedule"