from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from .config import settings
from . import models
from .base import Base

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
    try:
        with engine_without_db.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
            print(f" Database `{DATABASE_NAME}` verified if exist or created if it does not exist.")
    except OperationalError as e:
        print(" Failed to connect or create database:", e)
        raise


def create_tables_if_not_exists():
    try:
        Base.metadata.create_all(bind=engine)
        print(" Tables verified if exist or created if it does not exist.")
    except Exception as e:
        print(" Failed to create tables:", e)
        raise


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
