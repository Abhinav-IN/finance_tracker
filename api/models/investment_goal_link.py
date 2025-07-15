from sqlalchemy import Table, Column, Integer, ForeignKey
from api.database.base import Base

investment_goal_link = Table(
    "investment_goal_link",
    Base.metadata,
    Column("goal_id", Integer, ForeignKey("investmentGoal.goal_id", ondelete="CASCADE")),
    Column("investment_id", Integer, ForeignKey("investment.investment_id", ondelete="CASCADE"))
)
