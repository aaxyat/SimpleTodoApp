from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import dotenv

environ = dotenv.dotenv_values()

database_url = f"postgresql://{environ.get("POSTGRES_USER")}:{environ.get("POSTGRES_PASSWORD")}@{
    environ.get("POSTGRES_SERVER")}:{environ.get("POSTGRES_PORT")}/{environ.get("POSTGRES_DB")}"

SQLALCHEMY_DATABASE_URL = database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
