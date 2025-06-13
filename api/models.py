from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint, CheckConstraint
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)

    category = relationship('Category', back_populates='user')
    budgets = relationship('Budget', back_populates='user')
    transaction = relationship('Transaction', back_populates='user')

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    category_name = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='category')
    budget = relationship('Budget', back_populates='category')
    transaction = relationship('Transaction', back_populates='category')

class Budget(Base):
    __tablename__ = "budget"

    budget_id = Column(Integer, primary_key=True, nullable=True, autoincrement=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    category_id = Column(Integer, ForeignKey('categories.category_id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('user_id', 'category_id', name="uix_user_category"),
        CheckConstraint("start_date < end_date", name="Start_end_date_check")
    )

    user = relationship("User", back_populates="budgets")
    category = relationship("Category", back_populates="budgets")

class TransactionType(Base):
    __tablename__ = "transactiontype"

    transaction_type_id = Column(Integer, primary_key=True, nullable=False)
    transaction_type = Column(String(255), nullable=False)

    transaction = relationship('Transaction', back_populates='transaction_type')

class Transaction(Base):
    __tablename__ = "transaction"

    transaction_id = Column(Integer, primary_key=True, nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String(255), nullable=False)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id"), nullable=False)
    transaction_type_id = Column(Integer, ForeignKey("transactiontype.transaction_type_id"), nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="amount_check"),
    )

    user = relationship('User', back_populates='transaction')
    category = relationship('Category', back_populates='transaction')
    transaction_type = relationship('TransactionType', back_populates='transaction')


