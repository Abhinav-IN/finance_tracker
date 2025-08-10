from api.core.oauth2 import require_roles
from api.database.session import get_db
from api.models.investment import Investment
from api.models.transaction import Transaction
from api.schemas.investment import InvestmentRequest, investmentResponse, InvestmentQueryParam, InvestmentUpdateRequest, InvestmentWithdrawalRequest, PaginatedInvestmentResponse
from api.utils.investment import get_basic_data, calculate_current_value, calculate_gain_or_loss
from api.tasks.compound_task import calculate_compound_growth 
from api.services.lookup_create_service import get_or_create_category, get_or_create_paymentMode, get_or_create_transactionType, get_account_id
from datetime import datetime, time
from fastapi import Depends, status, HTTPException
from sqlalchemy.orm import Session
from zoneinfo import ZoneInfo

async def create_investment_service(
    user_investment: InvestmentRequest,
    user: dict = Depends(require_roles),
    db: Session = Depends(get_db)
):
    last_synced_at = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

    curr_price_per_unit = None
    gainOrLoss = None
    curr_value = None
 
    if user_investment.investment_type in ["mutual_fund", "stock", "etf","crypto"]:
        curr_price_per_unit = user_investment.buy_price_per_unit
        curr_value = calculate_current_value(user_investment.units, curr_price_per_unit)
        gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    elif user_investment.investment_type in ["fd", "bond"]:
        curr_value = calculate_compound_growth(
            principal=user_investment.amount_invested,
            interest_rate=user_investment.interest_rate,
            start_date=user_investment.investment_date,
            end_date=last_synced_at,
            frequency=user_investment.compounding_frequency
        )
        gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    else:
        curr_price_per_unit = user_investment.buy_price_per_unit or 0.0
        curr_value = calculate_current_value(user_investment.units or 1, curr_price_per_unit)
        gainOrLoss = calculate_gain_or_loss(curr_value, user_investment.amount_invested)

    account_id = get_account_id(user_investment.account_name, user["id"], db)

    new_investment = Investment(
        user_id=user["id"],
        account_linked=account_id,
        investment_name=user_investment.investment_name,
        investment_type=user_investment.investment_type,
        investment_date=user_investment.investment_date,
        description=user_investment.description,
        platform=user_investment.platform,
        amount_invested=user_investment.amount_invested,
        units=getattr(user_investment, "units", None),
        units_withdrawl=getattr(user_investment, "units_withdrawl", 0.0),
        buy_price_per_unit=getattr(user_investment, "buy_price_per_unit", None),
        maturity_date=getattr(user_investment, "maturity_date", None),
        interest_rate=getattr(user_investment, "interest_rate", None),
        compounding_frequency=getattr(user_investment, "compounding_frequency", None),
        current_price_per_unit=curr_price_per_unit,
        current_value=curr_value,
        status=user_investment.status,
        withdrawl_amount = user_investment.withdrawl_amount,
        withdrawl_date = user_investment.withdrawl_date,
        last_synced_at=last_synced_at,
        gain_or_loss=gainOrLoss
    )

    db.add(new_investment)
    try:
        db.commit()
        db.refresh(new_investment)
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Something went wrong in creating investment"
        )

    return investmentResponse.model_validate(new_investment)

def get_investment_service(
    filter_query: InvestmentQueryParam,
    user: dict = Depends(require_roles("user", "admin")),
    db: Session = Depends(get_db)
):
    curr_query = db.query(Investment).filter(Investment.user_id == user["id"])

    if filter_query.investment_id:
        curr_query = curr_query.filter(Investment.investment_id == filter_query.investment_id)
    if filter_query.investment_name:
        curr_query = curr_query.filter(Investment.investment_name.ilike(filter_query.investment_name.strip()))
    if filter_query.type:
        curr_query = curr_query.filter(Investment.investment_type.ilike(filter_query.type.strip()))
    if filter_query.investment_date:
        ist = ZoneInfo("Asia/Kolkata")
        start_of_day = datetime.combine(filter_query.investment_date, time.min).replace(tzinfo=ist)
        end_of_day = datetime.combine(filter_query.investment_date, time.max).replace(tzinfo=ist)
        curr_query = curr_query.filter(Investment.investment_date.between(start_of_day, end_of_day))
    if filter_query.platform:
        curr_query = curr_query.filter(Investment.platform.ilike(filter_query.platform.strip()))
    if filter_query.exact_amount:
        curr_query = curr_query.filter(Investment.amount_invested == filter_query.exact_amount)
    if filter_query.greater_amount:
        curr_query = curr_query.filter(Investment.amount_invested > filter_query.greater_amount)
    if filter_query.lower_amount:
        curr_query = curr_query.filter(Investment.amount_invested < filter_query.lower_amount)
    if filter_query.search:
        curr_query = curr_query.filter(Investment.description.ilike(f"%{filter_query.search}%"))

    total_records = curr_query.count()

    total_pages = (total_records + filter_query.limit - 1) // filter_query.limit
    paginated_query = curr_query.offset(filter_query.get_offset).limit(filter_query.limit).all()

    return PaginatedInvestmentResponse(
        total_pages=total_pages,
        current_page=filter_query.page,
        total_investments=total_records,
        investments=[investmentResponse.model_validate(i) for i in paginated_query]
    )

async def update_investment_service(investment_id: int,
                                    user_investment: InvestmentUpdateRequest,
                                    user: dict = Depends(require_roles("admin", "user")),
                                    db: Session = Depends(get_db)):
    curr_investment_query = db.query(Investment).filter(
        Investment.investment_id == investment_id,
        Investment.user_id == user["id"]
    )
    curr_investment = curr_investment_query.first()

    if not curr_investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment Not Found")

    last_synced_at = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    
    updated_curr_price_per_unit = None
    updated_current_value = None
    updated_gainOrLoss = None

    if user_investment.investment_type in ["mutual_fund", "stock", "etf", "crypto"]:
        units = user_investment.units - user_investment.units_withdrawl
        updated_curr_price_per_unit = user_investment.current_price_per_unit
        updated_current_value = calculate_current_value(units, updated_curr_price_per_unit)
        updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    elif user_investment.investment_type in ["fd", "bond"]:
        updated_current_value = calculate_compound_growth(
            principal=user_investment.amount_invested,
            interest_rate=user_investment.interest_rate,
            start_date=user_investment.investment_date,
            end_date=last_synced_at,
            frequency=user_investment.compounding_frequency
        )
        updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    else:
        updated_curr_price_per_unit = user_investment.current_price_per_unit
        updated_current_value = calculate_current_value(user_investment.units or 1, updated_curr_price_per_unit)
        updated_gainOrLoss = calculate_gain_or_loss(updated_current_value, user_investment.amount_invested)

    account_id = get_account_id(user_investment.account_name, user["id"], db)

    curr_investment_query.update({
        "investment_name": user_investment.investment_name,
        "investment_type": user_investment.investment_type,
        "investment_date": user_investment.investment_date,
        "account_linked": account_id,
        "description": user_investment.description,
        "platform": user_investment.platform,
        "amount_invested": user_investment.amount_invested,
        "units": getattr(user_investment, "units", None),
        "units_withdrawl":getattr(user_investment, "units_withdrawl", 0.0),
        "buy_price_per_unit": getattr(user_investment, "buy_price_per_unit", None),
        "maturity_date": getattr(user_investment, "maturity_date", None),
        "interest_rate": getattr(user_investment, "interest_rate", None),
        "compounding_frequency": getattr(user_investment, "compounding_frequency", None),
        "current_price_per_unit": updated_curr_price_per_unit,
        "current_value": updated_current_value,
        "status": user_investment.status,
        "withdrawl_amount": user_investment.withdrawl_amount,
        "withdrawl_date": user_investment.withdrawl_date,
        "last_synced_at": last_synced_at,
        "gain_or_loss": updated_gainOrLoss
    }, synchronize_session=False)

    try:
        db.commit()
        db.refresh(curr_investment)
    except Exception:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Something went wrong in updating investment")

    return investmentResponse.model_validate(curr_investment)



def delete_investment_service(investment_id: int,
                               user: dict = Depends(require_roles("user", "admin")),
                               db: Session = Depends(get_db)):
    investment = db.query(Investment).filter(Investment.investment_id == investment_id).first()

    if not investment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Investment not found")

    if user["role"] != "admin" and investment.user_id != user["id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own investment")

    db.delete(investment)
    db.commit()
    return

async def withdraw_investment_service(
    user_id: int,
    data: InvestmentWithdrawalRequest,
    db: Session
):
    investment = db.query(Investment).filter(
        Investment.investment_id == data.investment_id,
        Investment.user_id == user_id
    ).first()

    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")

    if not investment.units and investment.investment_type not in ["fd", "bond"]:
        raise HTTPException(status_code=400, detail="Units are not recorded for this investment")

    if investment.status == "fully_withdrawl":
        raise HTTPException(status_code=400, detail="Investment already fully withdrawn")

    current_price = investment.current_price_per_unit

    # ---------------- FD / Bond ----------------
    if investment.investment_type in ["fd", "bond"]:
        if data.withdraw_amount > investment.amount_invested:
            raise HTTPException(status_code=400, detail="Withdrawal exceeds invested amount")

        investment.withdrawl_amount = (investment.withdrawl_amount or 0) + data.withdraw_amount
        investment.amount_invested -= data.withdraw_amount
        investment.status = (
            "fully_withdrawl" if investment.amount_invested <= 0 else "partially_withdrawl"
        )
        investment.withdrawl_date = data.withdrawal_date
        investment.last_synced_at = datetime.now(tz=ZoneInfo("Asia/Kolkata"))

        # Create income transaction
        transaction_type, account_id = get_basic_data(data.investment_id, user_id, db)
        category_id = get_or_create_category("Investment", user_id, db)
        transaction_type_id = get_or_create_transactionType(transaction_type, user_id, db)
        payment_mode_id = get_or_create_paymentMode("Bank", user_id, db)

        new_income = Transaction(
            transaction_name=investment.investment_name,
            amount=data.withdraw_amount,
            description=f"Withdrawal from {investment.investment_type.upper()}",
            transaction_date=data.withdrawal_date,
            account_linked=account_id,
            user_id=user_id,
            category_id=category_id,
            transaction_type_id=transaction_type_id,
            payment_mode_id=payment_mode_id,
            is_expense=False,
            is_income=True
        )
        db.add(new_income)
        db.commit()
        db.refresh(investment)

        return {
            "message": "FD/Bond withdrawal successful",
            "withdrawn_amount": data.withdraw_amount,
            "status": investment.status
        }

    # ---------------- Stock / ETF / Crypto ----------------
    if not current_price or current_price <= 0:
        raise HTTPException(status_code=400, detail="Invalid current price")

    units_to_withdraw = round(data.withdraw_amount / current_price, 6)
    total_units = investment.units
    withdrawn_units = investment.units_withdrawl or 0
    available_units = total_units - withdrawn_units

    epsilon = 1e-6
    if units_to_withdraw - available_units > epsilon:
        max_withdrawable = round(available_units * current_price, 2)
        raise HTTPException(
            status_code=400,
            detail=f"Withdrawal exceeds available units. You can withdraw up to ₹{max_withdrawable} at current price ₹{current_price}"
        )

    investment.units_withdrawl = round(withdrawn_units + units_to_withdraw, 6)
    investment.withdrawl_amount = (investment.withdrawl_amount or 0) + data.withdraw_amount
    investment.withdrawl_date = data.withdrawal_date
    investment.last_synced_at = datetime.now(tz=ZoneInfo("Asia/Kolkata"))
    investment.current_value = calculate_current_value(
        total_units - investment.units_withdrawl, current_price
    )
    investment.status = (
        "fully_withdrawl" if investment.units_withdrawl >= total_units - epsilon else "partially_withdrawl"
    )

    # Create income transaction
    category_id = get_or_create_category("Investment", user_id, db)
    transaction_type_id = get_or_create_transactionType("Other", user_id, db)
    payment_mode_id = get_or_create_paymentMode("Bank", user_id, db)
    account_id = investment.account_linked

    new_income = Transaction(
        transaction_name=investment.investment_name,
        amount=data.withdraw_amount,
        description=f"Withdrawal from {investment.investment_type.upper()}",
        transaction_date=data.withdrawal_date,
        account_linked=account_id,
        user_id=user_id,
        category_id=category_id,
        transaction_type_id=transaction_type_id,
        payment_mode_id=payment_mode_id,
        is_expense=False,
        is_income=True
    )
    db.add(new_income)
    db.commit()
    db.refresh(investment)

    return {
        "message": "Withdrawal successful",
        "withdrawn_amount": data.withdraw_amount,
        "units_withdrawn": units_to_withdraw,
        "remaining_units": total_units - investment.units_withdrawl,
        "status": investment.status
    }
