from api.database.base import Base
from api.utils.enums import BillingPeriod
from api.utils.time import ist_now
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, Enum as sa_enum, ForeignKey, Float, Integer, String
from sqlalchemy.orm import relationship

class Subscription(Base):
    __tablename__ = "subscription"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(String(140), nullable=False)
    currency = Column(String(3), nullable=False)
    billing_period = Column(sa_enum(BillingPeriod, name="billing_period_enum"), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    next_billing_date = Column(DateTime(timezone=True), nullable=True)
    last_paid_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    account_id = Column(Integer, ForeignKey("account.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("transactiontype.id"), nullable=False)
    payment_mode_id = Column(Integer, ForeignKey("paymentmode.id"), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=ist_now)
    updated_at = Column(DateTime(timezone=True), default=ist_now, onupdate=ist_now)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_amount"),
    )

    user = relationship('User', back_populates='subscription')
    category = relationship('Category', back_populates='subscription')
    transaction_type = relationship('TransactionType', back_populates='subscription')
    payment_mode = relationship('PaymentMode', back_populates='subscription')
    account = relationship('Account', back_populates='subscription')