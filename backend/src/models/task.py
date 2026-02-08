"""
Background Task Model
Tracks async background tasks (scraping, batch processing, etc.)
"""

from sqlalchemy import Column, String, Text, DateTime, JSON
from datetime import datetime
import uuid
from enum import Enum

from core.database import Base


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class BackgroundTask(Base):
    """Background task tracking model."""
    
    __tablename__ = "background_tasks"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    task_type = Column(String(100), nullable=False)  # e.g., "scrape_jobs", "batch_match"
    status = Column(String(50), default=TaskStatus.PENDING)
    
    # Progress tracking
    progress = Column(String(255), nullable=True)  # e.g., "Processing 50/100 items"
    progress_percent = Column(String(10), default="0%")
    
    # Result storage
    result = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary representation."""
        return {
            "id": str(self.id),
            "task_type": self.task_type,
            "status": self.status,
            "progress": self.progress,
            "progress_percent": self.progress_percent,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def __repr__(self):
        return f"<BackgroundTask(id={self.id}, type='{self.task_type}', status='{self.status}')>"
