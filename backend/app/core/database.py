from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Configuration SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./satanas.db"

# Engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base Declarative
class Base(DeclarativeBase):
    pass
