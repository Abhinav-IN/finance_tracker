from api.database.base import Base
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from zoneinfo import ZoneInfo

class Account(Base):
    __tablename__ = "account"

    account_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_name = Column(String(104), nullable=False, unique=True)
    account_type = Column(String(104), nullable=False)
    bank_name = Column(String(104), nullable=True)
    balance_amount = Column(Float, nullable=False)
    is_active = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)

    __table_args__ = (
        CheckConstraint("balance_amount > 0", name="Balanace_amount_check"),
    )

    user = relationship('User', back_populates='account')
    transaction = relationship('Transaction', back_populates='account')
    subscription = relationship('Subscription', back_populates='account')
    investment = relationship('Investment', back_populates='account')