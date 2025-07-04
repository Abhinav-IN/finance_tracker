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
from api.core.config import settings

# engine = None
# engine_without_db = None
# SessionLocal = None


# def init_engines_and_session():
#     global engine, engine_without_db, SessionLocal
#     from api.core.config import settings  

#     DATABASE_NAME = settings.database_name

#     SQLALCHEMY_DATABASE_URL_WITHOUT_DB = (
#         f"mysql+pymysql://{settings.database_username}:{settings.database_password}"
#         f"@{settings.database_hostname}:{settings.database_port}"
#     )

#     SQLALCHEMY_DATABASE_URL = (
#         f"{SQLALCHEMY_DATABASE_URL_WITHOUT_DB}/{DATABASE_NAME}"
#     )

#     engine_without_db = create_engine(SQLALCHEMY_DATABASE_URL_WITHOUT_DB)
#     engine = create_engine(SQLALCHEMY_DATABASE_URL)
#     SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# def create_database_if_not_exists():
#     global engine_without_db
#     if engine_without_db is None:
#         init_engines_and_session()
#     try:
#         from api.core.config import settings  
#         with engine_without_db.connect() as conn:
#             conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {settings.database_name}"))
#             print(f" Database `{settings.database_name}` verified if exist or created if it does not exist.")
#     except OperationalError as e:
#         print(" Failed to connect or create database:", e)
#         raise


# def create_tables_if_not_exists():
#     global engine
#     if engine is None:
#         init_engines_and_session()
#     try:
#         Base.metadata.create_all(bind=engine)
#         print(" Tables verified if exist or created if it does not exist.")
#     except Exception as e:
#         print(" Failed to create tables:", e)
#         raise


# def get_db():
#     global SessionLocal
#     if SessionLocal is None:
#         init_engines_and_session()
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()



from api.logger import create_info_logger

database_logger = create_info_logger("Database Logger")

def get_timestamp():
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

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

def database_exists(db_name: str) -> bool:
    print("-----------------------------------------")
    try:
        with engine_without_db.connect() as connection:
            result = connection.execute(
                text("SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = :db_name"),
                {"db_name": db_name}
            ).fetchone()
            return result is not None
    except OperationalError as e:
        database_logger.info(f"Error connecting to MySQL server to check database existence: {e}")
        raise
    except ProgrammingError as e:
        database_logger.info(f"  Programming error during database existence check: {e}")
        raise
    except Exception as e:
        database_logger.info(f"  An unexpected error occurred during database existence check: {e}")
        raise

def tables_exist_in_db() -> bool:
    """
    Checks if tables defined in Base.metadata exist in the configured database.
    This is a basic check. It only verifies if *any* table defined in
    Base.metadata exists, not necessarily all of them or if they're up-to-date.
    For a more robust check (e.g., migrations), you'd use Alembic.

    Returns:
        True if at least one table defined in Base.metadata exists in the DB,
        False otherwise or if the database itself doesn't exist.
    """
    if not database_exists(DATABASE_NAME):
        database_logger.info(f"  Database '{DATABASE_NAME}' does not exist, so no tables can exist within it.")
        return False

    try:
        with engine.connect() as connection:
            inspector = connection.dialect.inspector(connection)
            existing_tables = inspector.get_table_names()
            for table_name in Base.metadata.tables.keys():
                if table_name in existing_tables:
                    database_logger.info(f"  Table '{table_name}' found in database.")
                    return True  # Found at least one, so assume tables are initialized
            return False # No tables from our models found
    except OperationalError as e:
        database_logger.info(f"  Error connecting to database '{DATABASE_NAME}' to check table existence: {e}")
        raise
    except Exception as e:
        database_logger.info(f"  An unexpected error occurred during table existence check: {e}")
        raise


# --- Database and Table Initialization Function ---
def init_db():
    database_logger.info(f"Attempting to initialize database '{DATABASE_NAME}'...")
    try:
        if not database_exists(DATABASE_NAME):
            database_logger.info(f"  Database '{DATABASE_NAME}' does not exist. Creating...")
            with engine_without_db.connect() as connection:
                connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}"))
                connection.commit()
            database_logger.info(f"  Database '{DATABASE_NAME}' created successfully.")
        else:
            database_logger.info(f"  Database '{DATABASE_NAME}' already exists.")
            database_logger.info(f"  Checking for existing tables and creating if necessary...")
        Base.metadata.create_all(bind=engine)
        database_logger.info(f"  Tables checked/created successfully.")

    except OperationalError as e:
        database_logger.info(f"  Failed to connect to MySQL server. Please check your connection string, " f"credentials, and ensure MySQL is running. Error: {e}")
        raise
    except Exception as e:
        database_logger.info(f"  An unexpected error occurred during database initialization: {e}")
        raise

# --- Dependency for FastAPI/Flask (common pattern) ---

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()