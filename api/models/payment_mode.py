from api.database.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class PaymentMode(Base):
    __tablename__ = "paymentmode"

    payment_mode_id = Column(Integer, primary_key=True, nullable=False)
    payment_mode = Column(String(255), nullable=False)

    transaction = relationship('Transaction', back_populates='payment_mode')
    subscription = relationship('Subscription', back_populates='payment_mode')