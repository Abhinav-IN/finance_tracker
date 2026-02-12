from api.database.base import Base
from api.utils.enums import UserRole
from datetime import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, Integer, JSON, String, Enum as sa_enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import TIMESTAMP
from zoneinfo import ZoneInfo

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)  
    user_name = Column(String(255), nullable=False, unique=True)
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
    failed_login_attempts = Column(Integer, default=0)
    last_failed_attempt_at = Column(TIMESTAMP(timezone=True), nullable=True)
    last_login_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    role = Column(sa_enum(UserRole, name="userrole"), nullable=False, default=UserRole.USER)


    category = relationship('Category', back_populates='user')
    budgets = relationship('Budget', back_populates='user')
    transactions = relationship('Transaction', back_populates='user')
    subscription = relationship('Subscription', back_populates='user')
    investment = relationship('Investment', back_populates='user')
    investment_goals = relationship('InvestmentGoal', back_populates='user')
    account = relationship('Account', back_populates='user')