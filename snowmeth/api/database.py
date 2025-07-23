"""Database models and session management for the API."""

import os
import uuid
from datetime import datetime
from typing import Dict, Any
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

Base = declarative_base()


class DbStory(Base):
    """SQLAlchemy model for stories."""

    __tablename__ = "stories"

    story_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    slug = Column(String, unique=True, nullable=False, index=True)
    story_idea = Column(Text, nullable=False)
    current_step = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Store steps as JSON for flexibility
    steps = Column(JSON, default=dict)

    # Store chapters as JSON for novel writing functionality
    chapters = Column(JSON, default=dict)

    # Writing style for chapter generation
    writing_style = Column(Text, nullable=True)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for compatibility with Story class."""
        return {
            "story_id": self.story_id,
            "slug": self.slug,
            "story_idea": self.story_idea,
            "current_step": self.current_step,
            "steps": self.steps or {},
            "chapters": self.chapters or {},
            "writing_style": self.writing_style,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DbTask(Base):
    """SQLAlchemy model for async tasks."""

    __tablename__ = "tasks"

    task_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    story_id = Column(String, ForeignKey("stories.story_id"), nullable=False)
    task_type = Column(String, nullable=False)  # 'next', 'refine', 'analyze', 'improve'
    status = Column(String, default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # Store task input/output as JSON
    input_data = Column(JSON, default=dict)
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    progress = Column(Integer, default=0)  # 0-100


# Database session management
class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str = None):
        if database_url is None:
            # Use DATABASE_PATH env var if set, otherwise default
            db_path = os.environ.get("DATABASE_PATH", "./data/snowmeth.db")
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            database_url = f"sqlite+aiosqlite:///{db_path}"

        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def get_session(self) -> AsyncSession:
        """Get a database session."""
        async with self.async_session() as session:
            yield session


# Global database manager instance
db_manager = DatabaseManager()
