"""
Database models and initialization.
"""

from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from src.core.config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SessionModel(Base):
    """AI Agent Session record."""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    agent_type = Column(String(50), nullable=False)  # claude, cursor, codex, etc.
    agent_version = Column(String(30), nullable=True)
    project_name = Column(String(200), nullable=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, default=0)
    
    # Token statistics
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    # Session metadata
    command_count = Column(Integer, default=0)
    file_changes = Column(Integer, default=0)
    error_count = Column(Integer, default=0)
    
    # Raw data storage
    session_data = Column(JSON, default=dict)
    tags = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CommandLog(Base):
    """Individual command log within a session."""
    __tablename__ = "command_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    command = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    duration_ms = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    command_type = Column(String(50), nullable=True)  # code, search, analysis, etc.


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
