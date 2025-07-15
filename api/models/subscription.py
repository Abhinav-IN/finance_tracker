from api.database.base import Base
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from zoneinfo import ZoneInfo

class Subscription(Base):
    __tablename__ = "subscription"

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    subscription_name = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(140), nullable=False)
    currency = Column(String(3), nullable=False)
    billing_cycle = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("transactiontype.transaction_type_id"), nullable=False)
    payment_mode_id = Column(Integer, ForeignKey("paymentmode.payment_mode_id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    last_paid_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_amount"),
    )

    user = relationship('User', back_populates='subscription')
    category = relationship('Category', back_populates='subscription')
    transaction_type = relationship('TransactionType', back_populates='subscription')
    payment_mode = relationship('PaymentMode', back_populates='subscription')

