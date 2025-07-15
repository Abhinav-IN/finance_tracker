from api.database.base import Base
from datetime import datetime
from sqlalchemy import (
    Boolean, CheckConstraint, Column, DateTime, Float, 
    ForeignKey, Integer, String
)
from sqlalchemy.orm import relationship
from zoneinfo import ZoneInfo
from api.models.investment_goal_link import investment_goal_link  

class InvestmentGoal(Base):
    __tablename__ = "investmentGoal"

    goal_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    goal_name = Column(String(104), nullable=False)
    description = Column(String(255), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    goal_amount = Column(Float, nullable=False)
    applies_to_all_investments = Column(Boolean, default=True)
    current_value = Column(Float, default=0)
    is_completed = Column(Boolean, default=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
        nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
        onupdate=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
        nullable=False
    )

    __table_args__ = (
        CheckConstraint("start_date < end_date", name="Start_end_date_check"),
        CheckConstraint("goal_amount > 0", name="goal_amount_check"),
    )

    user = relationship("User", back_populates="investment_goals")

    investments = relationship(
        "Investment",
        secondary=investment_goal_link,
        back_populates="goals"
    )
