"""
Job Model
Stores job descriptions with vector embeddings for semantic search.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime
import uuid

from core.database import Base
from core.config import settings


class Job(Base):
    """Job description model with vector embedding."""
    
    __tablename__ = "jobs"
    
    # Use String for UUID to work with both PostgreSQL and SQLite
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)
    
    # Store skills as JSON (works with both DBs)
    skills = Column(JSON, default=[])
    
    # Vector embedding stored as JSON for SQLite compatibility
    # For PostgreSQL with pgvector, we can use native Vector type in a migration
    embedding = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "title": self.title,
            "company": self.company,
            "description": self.description[:500] if self.description else "",
            "skills": self.skills or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}')>"
