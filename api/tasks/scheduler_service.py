from api.tasks.subscription import get_next_billing_date
from api.utils.investment import sync_all_investments, update_all_investment_goal_values, update_fd_and_bond_values
from api.tasks.celery_worker import celery_app

@celery_app.task(name="api.tasks.scheduler_service.run_daily_subscription_job")
def run_daily_subscription_job():
    get_next_billing_date()

@celery_app.task(name="api.tasks.scheduler_service.run_daily_investment_sync")
def run_daily_investment_sync():
    sync_all_investments()

@celery_app.task(name="api.tasks.scheduler_service.run_hourly_goal_value_update")
def run_hourly_goal_value_update():
    update_all_investment_goal_values()

@celery_app.task(name="api.tasks.scheduler_service.run_daily_fd_and_bond_update")
def run_daily_fd_and_bond_update():
    update_fd_and_bond_values()
   