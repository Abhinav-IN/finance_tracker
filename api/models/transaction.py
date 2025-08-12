from api.database.base import Base
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from zoneinfo import ZoneInfo

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, nullable=False)
    transaction_name = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(140), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    account_linked = Column(Integer, ForeignKey("account.account_id"),  nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("transactiontype.transaction_type_id"), nullable=False)
    is_expense = Column(Boolean, nullable=False)
    is_income = Column(Boolean, nullable=False)
    payment_mode_id = Column(Integer, ForeignKey("paymentmode.payment_mode_id"), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_check"),
    )

    user = relationship('User', back_populates='transaction')
    category = relationship('Category', back_populates='transactions')
    transaction_type = relationship('TransactionType', back_populates='transaction')
    payment_mode = relationship('PaymentMode', back_populates='transaction')
    account = relationship('Account', back_populates='transaction')
