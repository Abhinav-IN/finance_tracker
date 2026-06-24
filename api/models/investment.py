from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, CheckConstraint, Enum as SQLEnum
from sqlalchemy.orm import relationship
from api.database.base import Base
from api.utils.enums import InvestmentType, InvestmentStatus
from api.utils.time import ist_now

class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    investment_type = Column(SQLEnum(InvestmentType, name="investment_type_enum"), nullable=False)
    platform = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    units = Column(Float, nullable=True)
    buy_price = Column(Float, nullable=True)
    date = Column(DateTime(timezone=True), nullable=False)
    description = Column(String(140), nullable=True)
    status = Column(SQLEnum(InvestmentStatus, name="investment_status_enum"), default=InvestmentStatus.ACTIVE, nullable=False)
    created_at = Column(DateTime(timezone=True), default=ist_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=ist_now, onupdate=ist_now, nullable=False)

    __table_args__ = (
        CheckConstraint("amount > 0", name="chk_invested_amount"),
        CheckConstraint("units IS NULL OR units >= 0", name="chk_units"),
        CheckConstraint("buy_price IS NULL OR buy_price >= 0", name="chk_buy_price"),
    )

    user = relationship("User", back_populates="investments")
    prices = relationship("InvestmentPrice", back_populates="investment", cascade="all, delete-orphan",order_by="InvestmentPrice.recorded_at.desc()")
