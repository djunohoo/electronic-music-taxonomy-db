"""
Database configuration and session management.
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.models import Base

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///taxonomy.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv('DEBUG') else False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all database tables."""
    Base.metadata.create_all(bind=engine)

def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database with tables."""
    create_tables()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_database()