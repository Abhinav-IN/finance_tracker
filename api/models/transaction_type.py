from api.database.base import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class TransactionType(Base):
    __tablename__ = "transactiontype"

    transaction_type_id = Column(Integer, primary_key=True, nullable=False)
    transaction_type = Column(String(255), nullable=False)

    transaction = relationship('Transaction', back_populates='transaction_type')
    subscription = relationship('Subscription', back_populates='transaction_type')
