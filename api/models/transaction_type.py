from api.database.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class TransactionType(Base):
    __tablename__ = "transactiontype"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(255), nullable=False)

    transactions = relationship('Transaction', back_populates='transaction_type')
    subscription = relationship('Subscription', back_populates='transaction_type')
