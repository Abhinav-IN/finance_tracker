from api.tasks.subscription import get_next_billing_date
from api.utils.investment import sync_stock_and_etf_prices, update_all_investment_goal_values, update_fd_and_bond_values, sync_crypto_prices
from api.tasks.celery_worker import celery_app

@celery_app.task(name="api.tasks.scheduler_service.run_daily_subscription_job")
def run_daily_subscription_job():
    get_next_billing_date()

@celery_app.task(name="api.tasks.scheduler_service.run_hourly_goal_value_update")
def run_hourly_goal_value_update():
    update_all_investment_goal_values()

@celery_app.task(name="api.tasks.scheduler_service.run_daily_fd_and_bond_update")
def run_daily_fd_and_bond_update():
    update_fd_and_bond_values()

@celery_app.task(name="api.tasks.scheduler_service.run_daily_stock_price_update")
def run_daily_stock_price_update():
    sync_stock_and_etf_prices()

@celery_app.task(name="api.tasks.scheduler_service.run_daily_crypto_price_update")
def run_daily_crypto_price_update():
    sync_crypto_prices()

   