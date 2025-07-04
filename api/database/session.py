from api.database.base import Base
from api.models.user import User
from api.models.category import Category
from api.models.transaction_type import TransactionType
from api.models.payment_mode import PaymentMode
from api.models.budget import Budget
from api.models.transaction import Transaction
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

engine = None
engine_without_db = None
SessionLocal = None


def init_engines_and_session():
    global engine, engine_without_db, SessionLocal
    from api.core.config import settings  

    DATABASE_NAME = settings.database_name

    SQLALCHEMY_DATABASE_URL_WITHOUT_DB = (
        f"mysql+pymysql://{settings.database_username}:{settings.database_password}"
        f"@{settings.database_hostname}:{settings.database_port}"
    )

    SQLALCHEMY_DATABASE_URL = (
        f"{SQLALCHEMY_DATABASE_URL_WITHOUT_DB}/{DATABASE_NAME}"
    )

    engine_without_db = create_engine(SQLALCHEMY_DATABASE_URL_WITHOUT_DB)
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_database_if_not_exists():
    global engine_without_db
    if engine_without_db is None:
        init_engines_and_session()
    try:
        from api.core.config import settings  
        with engine_without_db.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.database_name}"))
            print(f" Database `{settings.database_name}` verified if exist or created if it does not exist.")
    except OperationalError as e:
        print(" Failed to connect or create database:", e)
        raise


def create_tables_if_not_exists():
    global engine
    if engine is None:
        init_engines_and_session()
    try:
        Base.metadata.create_all(bind=engine)
        print(" Tables verified if exist or created if it does not exist.")
    except Exception as e:
        print(" Failed to create tables:", e)
        raise


def get_db():
    global SessionLocal
    if SessionLocal is None:
        init_engines_and_session()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
