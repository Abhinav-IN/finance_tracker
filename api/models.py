from .database import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String(256), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    date_joined = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))

