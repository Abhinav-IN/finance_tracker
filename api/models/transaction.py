from api.database.base import Base
from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("transactiontype.transaction_type_id"), nullable=False)
    payment_mode_id = Column(Integer, ForeignKey("paymentmode.payment_mode_id"), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_check"),
    )

    user = relationship('User', back_populates='transaction')
    category = relationship('Category', back_populates='transactions')
    transaction_type = relationship('TransactionType', back_populates='transaction')
    payment_mode = relationship('PaymentMode', back_populates='transaction')
