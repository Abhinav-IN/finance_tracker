from api.models.category import Category
from api.models.payment_mode import PaymentMode
from api.models.transaction_type import TransactionType
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def get_or_create_category(categoryName: str, userId: int, db: Session) -> int:
    existing = db.query(Category).filter(
        Category.user_id == userId,
        Category.category_name.ilike(categoryName.strip())
    ).first()

    if existing:
        return existing.category_id

    new_category = Category(category_name=categoryName.strip(), user_id=userId)
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    return new_category.category_id


def get_or_create_transactionType(transactionTypeName: str, userId: int, db: Session) -> int:
    existing = db.query(TransactionType).filter(
        TransactionType.transaction_type.ilike(transactionTypeName.strip())
    ).first()

    if existing:
        return existing.transaction_type_id

    new_transaction_type = TransactionType(transaction_type=transactionTypeName.strip())
    db.add(new_transaction_type)
    try:
        db.commit()
        db.refresh(new_transaction_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction type name already exists"
        )
    return new_transaction_type.transaction_type_id


def get_or_create_paymentMode(paymentModeName: str, userId: int, db: Session) -> int:
    existing = db.query(PaymentMode).filter(
        PaymentMode.payment_mode.ilike(paymentModeName.strip())
    ).first()

    if existing:
        return existing.payment_mode_id

    new_payment_mode = PaymentMode(payment_mode=paymentModeName.strip())
    db.add(new_payment_mode)
    try:
        db.commit()
        db.refresh(new_payment_mode)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment mode name already exists"
        )
    return new_payment_mode.payment_mode_id
