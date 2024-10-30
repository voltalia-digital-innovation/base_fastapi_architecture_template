import urllib
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from modules.core.env import (
    DB_USER, DB_PASSWORD, DB_HOST, DB_NAME, DB_PORT
)

"""
Database configuration file. SQLAlchemy as ORM and Pydantic as serializer

Author: Matheus Henrique (m.araujo)

Date: 3th September 2024
"""
password = urllib.parse.quote_plus(str(DB_PASSWORD))
# SQLite used just to test porpouses
SQLALCHEMY_DATABASE_URL = f'mssql+pyodbc://{DB_USER}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC Driver 17 for SQL Server'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
