"""
Resume Model
Stores candidate resumes with vector embeddings for semantic matching.
"""

from sqlalchemy import Column, String, Text, DateTime, JSON
from datetime import datetime
import uuid

from core.database import Base
from core.config import settings


class Resume(Base):
    """Resume/candidate model with vector embedding."""
    
    __tablename__ = "resumes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    
    # Store skills as JSON
    skills = Column(JSON, default=[])
    
    # Vector embedding stored as JSON for SQLite compatibility
    embedding = Column(JSON, nullable=True)
    
    # Original file info
    filename = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "content": self.content[:500] if self.content else "",
            "skills": self.skills or [],
            "filename": self.filename,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def __repr__(self):
        return f"<Resume(id={self.id}, name='{self.name}')>"
