from api.database.base import Base
from sqlalchemy import CheckConstraint, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from api.utils.time import ist_now
from api.utils.enums import TransactionDirection

class Transaction(Base):
    __tablename__ = "transactions"  # Changed table name from transaction to transactions

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String(64), nullable=False) # Changed name from transaction_name to title
    amount = Column(Numeric(12, 2), nullable=False)  # Changed type from float to Numeric to avoid floating point imprecesion
    description = Column(String(140), nullable=True) # Made description nullable
    date = Column(DateTime(timezone=True), nullable=False)
    account_id = Column(Integer, ForeignKey("account.id"),  nullable=True) # CHanged name from account_linked to account_id
    created_at = Column(DateTime(timezone=True), default=ist_now, nullable=False) # Added the ist_now logic in util
    updated_at = Column(DateTime(timezone=True), default=ist_now, onupdate=ist_now, nullable=False) # Added the ist_now logic in util fn
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("transactiontype.id"), nullable=False)
    direction = Column(SQLEnum(TransactionDirection, name="transaction_direction_enum"), nullable = False) # Combined logic of is_income and is_expense into this.
    payment_mode_id = Column(Integer, ForeignKey("paymentmode.id"), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_transaction_amount_positive"), # Changed name of the constraint
    )

    # Updated table name to transactions
    user = relationship('User', back_populates='transactions')
    category = relationship('Category', back_populates='transactions')
    transaction_type = relationship('TransactionType', back_populates='transactions')
    payment_mode = relationship('PaymentMode', back_populates='transactions')
    account = relationship('Account', back_populates='transactions')
