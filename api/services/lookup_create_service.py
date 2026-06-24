from api.models.category import Category
from api.models.payment_mode import PaymentMode
from api.models.transaction_type import TransactionType
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

def get_or_create_category(categoryName: str, userId: int, db: Session) -> int:
    existing = db.query(Category).filter(Category.user_id == userId, Category.name.ilike(categoryName.strip())).first()

    if existing:
        return existing.id

    new_category = Category(name=categoryName.strip(), user_id=userId)
    db.add(new_category)
    try:
        db.commit()
        db.refresh(new_category)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    return new_category.id

def get_or_create_transactionType(transactionTypeName: str, db: Session) -> int:
    existing = db.query(TransactionType).filter(TransactionType.name.ilike(transactionTypeName.strip())).first()

    if existing:
        return existing.id

    new_transaction_type = TransactionType(name=transactionTypeName.strip())
    db.add(new_transaction_type)
    try:
        db.commit()
        db.refresh(new_transaction_type)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction type name already exists")
    
    return new_transaction_type.id


def get_or_create_paymentMode(paymentModeName: str, db: Session) -> int:
    existing = db.query(PaymentMode).filter(PaymentMode.name.ilike(paymentModeName.strip())).first()

    if existing:
        return existing.id

    new_payment_mode = PaymentMode(name=paymentModeName.strip())
    db.add(new_payment_mode)
    try:
        db.commit()
        db.refresh(new_payment_mode)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment mode name already exists")
    return new_payment_mode.id