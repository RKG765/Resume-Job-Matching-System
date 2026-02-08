"""
Database Service
CRUD operations for jobs and resumes with vector search.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
import numpy as np

from models.job import Job
from models.resume import Resume
from models.task import BackgroundTask, TaskStatus
from services.embedding_service import get_embedding_service
from classification.skill_gap import SkillGapAnalyzer
from core.config import settings

logger = logging.getLogger(__name__)



class DatabaseService:
    """Database operations for jobs and resumes."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.embedding_service = get_embedding_service()
        self.skill_analyzer = SkillGapAnalyzer()
    
    # ==================== Job Operations ====================
    
    async def create_job(self, title: str, company: str, description: str, 
                         skills: Optional[List[str]] = None) -> Job:
        """Create a new job with embedding."""
        # Extract skills if not provided
        if not skills:
            skills = list(self.skill_analyzer.extract_skills(description))
        
        # Generate embedding
        embedding = self.embedding_service.encode(description)
        
        job = Job(
            title=title,
            company=company,
            description=description,
            skills=skills,
            embedding=embedding
        )
        
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        logger.info(f"Created job: {job.id} - {title}")
        return job
    
    async def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        return result.scalar_one_or_none()
    
    async def get_jobs(self, limit: int = 100, offset: int = 0) -> List[Job]:
        """Get all jobs with pagination."""
        result = await self.db.execute(
            select(Job).order_by(Job.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_jobs(self) -> int:
        """Count total jobs."""
        result = await self.db.execute(select(func.count(Job.id)))
        return result.scalar() or 0
    
    async def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        job = await self.get_job(job_id)
        if job:
            await self.db.delete(job)
            await self.db.commit()
            return True
        return False
    
    # ==================== Resume Operations ====================
    
    async def create_resume(self, name: str, content: str, 
                           email: Optional[str] = None,
                           skills: Optional[List[str]] = None,
                           filename: Optional[str] = None) -> Resume:
        """Create a new resume with embedding."""
        # Extract skills if not provided
        if not skills:
            skills = list(self.skill_analyzer.extract_skills(content))
        
        # Generate embedding
        embedding = self.embedding_service.encode(content)
        
        resume = Resume(
            name=name,
            email=email,
            content=content,
            skills=skills,
            embedding=embedding,
            filename=filename
        )
        
        self.db.add(resume)
        await self.db.commit()
        await self.db.refresh(resume)
        
        logger.info(f"Created resume: {resume.id} - {name}")
        return resume
    
    async def get_resume(self, resume_id: str) -> Optional[Resume]:
        """Get a resume by ID."""
        result = await self.db.execute(select(Resume).where(Resume.id == resume_id))
        return result.scalar_one_or_none()
    
    async def get_resumes(self, limit: int = 100, offset: int = 0) -> List[Resume]:
        """Get all resumes with pagination."""
        result = await self.db.execute(
            select(Resume).order_by(Resume.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_resumes(self) -> int:
        """Count total resumes."""
        result = await self.db.execute(select(func.count(Resume.id)))
        return result.scalar() or 0
    
    async def delete_resume(self, resume_id: str) -> bool:
        """Delete a resume."""
        resume = await self.get_resume(resume_id)
        if resume:
            await self.db.delete(resume)
            await self.db.commit()
            return True
        return False
    
    # ==================== Vector Search Operations ====================
    
    async def find_similar_resumes(self, job_description: str, 
                                   limit: int = 10) -> List[tuple[Resume, float]]:
        """
        Find resumes similar to a job description using semantic search.
        This is where BERT shines - it understands meaning, not just words.
        """
        # Generate embedding for job
        job_embedding = self.embedding_service.encode(job_description)
        
        # Use pgvector's cosine distance for similarity search
        # Note: pgvector uses distance (lower = better), we convert to similarity
        if not settings.USE_SQLITE:
            # PostgreSQL with pgvector
            query = text("""
                SELECT id, name, content, skills, 
                       1 - (embedding <=> :embedding) as similarity
                FROM resumes
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = await self.db.execute(
                query, 
                {"embedding": str(job_embedding), "limit": limit}
            )
            rows = result.fetchall()
            
            results = []
            for row in rows:
                resume = await self.get_resume(row[0])
                if resume:
                    results.append((resume, float(row[4])))
            return results
        else:
            # SQLite fallback - compute similarity in Python
            resumes = await self.get_resumes(limit=1000)
            candidates = [(r.content, r) for r in resumes if r.embedding]
            
            if not candidates:
                return []
            
            similarities = self.embedding_service.batch_similarity(
                job_description,
                [c[0] for c in candidates]
            )
            
            results = list(zip([c[1] for c in candidates], similarities))
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
    
    async def find_similar_jobs(self, resume_content: str, 
                                limit: int = 10) -> List[tuple[Job, float]]:
        """Find jobs similar to a resume using semantic search."""
        resume_embedding = self.embedding_service.encode(resume_content)
        
        if not settings.USE_SQLITE:
            query = text("""
                SELECT id, title, description, skills,
                       1 - (embedding <=> :embedding) as similarity
                FROM jobs
                WHERE embedding IS NOT NULL
                ORDER BY embedding <=> :embedding
                LIMIT :limit
            """)
            
            result = await self.db.execute(
                query,
                {"embedding": str(resume_embedding), "limit": limit}
            )
            rows = result.fetchall()
            
            results = []
            for row in rows:
                job = await self.get_job(row[0])
                if job:
                    results.append((job, float(row[4])))
            return results
        else:
            jobs = await self.get_jobs(limit=1000)
            candidates = [(j.description, j) for j in jobs if j.embedding]
            
            if not candidates:
                return []
            
            similarities = self.embedding_service.batch_similarity(
                resume_content,
                [c[0] for c in candidates]
            )
            
            results = list(zip([c[1] for c in candidates], similarities))
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
    
    # ==================== Task Operations ====================
    
    async def create_task(self, task_type: str) -> BackgroundTask:
        """Create a new background task."""
        task = BackgroundTask(
            task_type=task_type,
            status=TaskStatus.PENDING
        )
        self.db.add(task)
        await self.db.commit()
        await self.db.refresh(task)
        return task
    
    async def get_task(self, task_id: str) -> Optional[BackgroundTask]:
        """Get a task by ID."""
        result = await self.db.execute(
            select(BackgroundTask).where(BackgroundTask.id == task_id)
        )
        return result.scalar_one_or_none()
    
    async def update_task(self, task_id: str, **kwargs) -> Optional[BackgroundTask]:
        """Update a task."""
        task = await self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            await self.db.commit()
            await self.db.refresh(task)
        return task
