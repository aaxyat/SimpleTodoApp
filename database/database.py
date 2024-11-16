from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import dotenv
import os

environ = dotenv.dotenv_values()

# Build PostgreSQL URL if environment variables are present
if environ and all(key in environ for key in [
    "POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_SERVER",
    "POSTGRES_PORT", "POSTGRES_DB"
]):
    database_url = (
        f"postgresql://{environ['POSTGRES_USER']}:"
        f"{environ['POSTGRES_PASSWORD']}@{environ['POSTGRES_SERVER']}:"
        f"{environ['POSTGRES_PORT']}/{environ['POSTGRES_DB']}"
    )
else:
    # Fallback to SQLite if .env is not present or incomplete
    sqlite_db_path = os.path.join(os.path.dirname(__file__), "sqlite.db")
    database_url = f"sqlite:///{sqlite_db_path}"

SQLALCHEMY_DATABASE_URL = database_url

# Create engine with special args for SQLite
connect_args = {"check_same_thread": False} if database_url.startswith("sqlite") else {}
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
