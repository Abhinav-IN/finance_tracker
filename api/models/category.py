from api.database.base import Base
import sqlalchemy as sa
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    category_name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    __table_args__ = (
        sa.UniqueConstraint("user_id", "category_name", name="uix_user_category"),
    )

    user = relationship('User', back_populates='category')
    budgets = relationship('Budget', back_populates='category')
    transactions = relationship('Transaction', back_populates='category')
    subscription = relationship('Subscription', back_populates='category')