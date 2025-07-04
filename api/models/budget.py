from api.database.base import Base
from sqlalchemy import CheckConstraint, Column, Date, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship


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