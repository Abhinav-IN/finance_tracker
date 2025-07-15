from celery.schedules import crontab

# Use `celery.conf.beat_schedule` not `CELERY_BEAT_SCHEDULE`
beat_schedule = {
    "run-daily-subscription-job": {
        "task": "api.tasks.scheduler_service.run_daily_subscription_job",
        "schedule": crontab(hour=18, minute=31),  # Every 1 min for testing
    },
    "run-daily-investment-sync": {
        "task": "api.tasks.scheduler_service.run_daily_investment_sync",
        "schedule": crontab(hour=1, minute=0),
    },
    "run-hourly-goal-value-update": {
        "task": "api.tasks.scheduler_service.run_hourly_goal_value_update",
        "schedule": crontab(minute=0),
    },
    # ✅ New: FD and Bond compounding updater
    "run-daily-fd-and-bond-update": {
        "task": "api.tasks.scheduler_service.update_fd_and_bond_values",  # make sure this matches your actual import path
        "schedule": crontab(hour=8, minute=35),  # Daily at 2:00 AM
    },
}

timezone = "Asia/Kolkata"
beat_schedule_filename = "/app/celery-beat/celerybeat-schedule"
