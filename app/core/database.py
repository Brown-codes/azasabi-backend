# app/core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# The Engine is the core interface to the database
engine = create_engine(settings.SUPABASE_DB_URL)

# A Session is a temporary workspace for your database operations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all our future database models
Base = declarative_base()

# Dependency for FastAPI to get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()