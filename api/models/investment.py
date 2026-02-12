from api.database.base import Base
from api.models.investment_goal_link import investment_goal_link
from sqlalchemy import CheckConstraint, Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from zoneinfo import ZoneInfo

class Investment(Base):
    __tablename__ = "investment"

    investment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    investment_name = Column(String(104), nullable=False)
    investment_type = Column(String(104), nullable=False)
    investment_date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(255), nullable=False)
    platform = Column(String(104), nullable=False)
    amount_invested = Column(Float, nullable=False)
    units = Column(Float, nullable=True)
    account_linked = Column(Integer, ForeignKey("account.id"), nullable=True)
    buy_price_per_unit = Column(Float, nullable=True)
    maturity_date = Column(DateTime(timezone=True), nullable=True)
    current_price_per_unit = Column(Float, nullable=True)
    current_value = Column(Float, nullable=True)
    gain_or_loss = Column(Float, nullable=True)
    interest_rate = Column(Float, nullable=True)
    compounding_frequency = Column(String(104), nullable=True)
    status = Column(String(255), nullable=False)
    withdrawl_amount = Column(Float, nullable=True)
    withdrawl_date = Column(DateTime(timezone=True), nullable=True)
    units_withdrawl = Column(Float, nullable=True)
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")), nullable=False)

    __table_args__ = (
        CheckConstraint("amount_invested > 0", name="Amount invested check"),
        CheckConstraint("buy_price_per_unit >= 0", name="Buying price of unit check"),
        CheckConstraint("current_price_per_unit IS NULL OR current_price_per_unit >= 0", name="Current price check"),
        CheckConstraint("current_value IS NULL OR current_value >= 0", name="Current value check"),

    )

    user = relationship('User', back_populates='investment')
    goals = relationship(
        "InvestmentGoal",
        secondary=investment_goal_link,
        back_populates="investments"
    )
    account = relationship('Account', back_populates='investment')