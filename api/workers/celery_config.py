from celery.schedules import crontab

beat_schedule = {
    "run-daily-subscription-job": {
        "task": "api.tasks.scheduler_service.run_daily_subscription_job",
        "schedule": crontab(hour=18, minute=31),  
    },
    "run-hourly-goal-value-update": {
        "task": "api.tasks.scheduler_service.run_hourly_goal_value_update",
        "schedule": crontab(minute=0),
    },
   "run-daily-fd-and-bond-update": {
        "task": "api.tasks.scheduler_service.run_daily_fd_and_bond_update",  
        "schedule": crontab(hour=8, minute=35),
    },
    "run-daily-stock-and-etf-update":{
        "task": "api.tasks.scheduler_service.run_daily_stock_price_update",
        "schedule": crontab(hour=10, minute=0)
    },
    "run-daily-crypto-price-update":{
        "task": "api.tasks.scheduler_service.run_daily_crypto_price_update",
        "schedule": crontab(hour=10, minute=0)
    },
}

timezone = "Asia/Kolkata"
beat_schedule_filename = "/app/celery-beat/celerybeat-schedule"
