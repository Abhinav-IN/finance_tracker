from .database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, UniqueConstraint, CheckConstraint, Boolean, JSON
from sqlalchemy.sql.sqltypes import TIMESTAMP
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import Enum as sa_enum

class UserRole(str, enum.Enum):
    user = "user"
    admin = "admin"
    moderator = "moderator"
    support = "support"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)  
    username = Column(String(255), nullable=False, unique=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True)
    dob = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)  
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_suspended = Column(Boolean, default=False)
    last_password_change_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_five_passwords = Column(JSON, nullable=True)  
    password_reset_token_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    account_verification_token_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)
    login_attempts = Column(Integer, default=0)
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'), onupdate=text('now()'))
    role = Column(sa_enum(UserRole, name="userrole"), nullable=False, default=UserRole.user)


    category = relationship('Category', back_populates='user')
    budgets = relationship('Budget', back_populates='user')
    transaction = relationship('Transaction', back_populates='user')

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    category_name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship('User', back_populates='category')
    budgets = relationship('Budget', back_populates='category')
    transactions = relationship('Transaction', back_populates='category')

class Budget(Base):
    __tablename__ = "budget"

    budget_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
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
    category = relationship('Category', back_populates='transactions')
    transaction_type = relationship('TransactionType', back_populates='transaction')


