from datetime import datetime
from faker import Faker
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from api.database.session import get_db
from api.models.user import User
from api.models.transaction import Transaction
from api.models.budget import Budget
from api.utils.hashing import hashing_password
from api.services.lookup_create_service import (
    get_or_create_category,
    get_or_create_paymentMode,
    get_or_create_transactionType,
)
from fastapi import APIRouter, Depends

router = APIRouter(tags=['Seeding'], prefix='/api/v1/seed')
fake = Faker()
user_password = "TestPassword123!"

@router.post("/test-user-data")
def seed_test_user_data(db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email="testuser@example.com").first()
    if not user:
        try:
            user = User(
                username="testuser",
                email="testuser@example.com",
                first_name="Test",
                last_name="User",
                hashed_password=hashing_password(user_password),
                gender="other",
                dob=datetime(2000, 1, 1).date(),
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creating dummy user")

    user_id = user.id

    transaction_types = ["salary", "rent", "nil", "other"]
    payment_modes = ["cash", "credit card", "upi"]

    for ttype in transaction_types:
        get_or_create_transactionType(ttype, user_id, db)

    for mode in payment_modes:
        get_or_create_paymentMode(mode, user_id, db)

    categories = ["groceries", "bills", "rent", "games", "fees", "party"]
    category_ids = {}

    for cname in categories:
        category_id = get_or_create_category(cname, user_id, db)
        category_ids[cname] = category_id

    for cname in categories:
        exists = db.query(Budget).filter(
            Budget.user_id == user_id,
            Budget.category_id == category_ids[cname]
        ).first()

        if not exists:
            try:
                budget = Budget(
                    user_id=user_id,
                    category_id=category_ids[cname],
                    budget_amount=fake.random_int(min=2000, max=10000),
                    start_date=datetime(2026, 1, 15).date(),
                    end_date=datetime(2026, 2, 15).date(),
                )
                db.add(budget)
                db.commit()
                db.refresh(budget)
            
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong in creating Budget for dummy user")


    for _ in range(400):
        category_name = fake.random_element(elements=categories)
        category_id = category_ids[category_name]
        transaction_type = fake.random_element(elements=transaction_types)
        payment_mode = fake.random_element(elements=payment_modes)

        try:
            new_transaction = Transaction(
                title=fake.word(),
                amount=fake.random_int(min=100, max=500),
                description=fake.sentence(),
                transaction_date=fake.date_time_between(start_date="-10d", end_date="now"),
                user_id=user_id,
                category_id=category_id,
                transaction_type_id=get_or_create_transactionType(transaction_type, user_id, db),
                payment_mode_id=get_or_create_paymentMode(payment_mode, user_id, db),
                direction="EXPENSE"
            )
            db.add(new_transaction)
            db.commit()
            db.refresh(new_transaction)
        
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something went wrong while creating dummy transaction")

    return {"message": "Test user and seed data created successfully.",
            "user_name" : user.username,
            "user_password" : user_password,
            "user_mail" : user.email}
