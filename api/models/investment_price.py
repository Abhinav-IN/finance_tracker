from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from api.database.base import Base
from api.utils.time import ist_now

class InvestmentPrice(Base):
    __tablename__ = "investment_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    investment_id = Column(Integer, ForeignKey("investments.id", ondelete="CASCADE"), nullable=False)
    price_per_unit = Column(Float, nullable=False)
    total_value = Column(Float, nullable=True)
    recorded_at = Column(DateTime(timezone=True), default=ist_now, nullable=False)

    __table_args__ = (
        CheckConstraint("price_per_unit > 0", name="chk_price_positive"),
    )

    investment = relationship(
        "Investment",
        back_populates="prices"
    )
