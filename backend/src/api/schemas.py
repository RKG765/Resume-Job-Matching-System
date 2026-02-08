"""
API Schemas (Pydantic Models)
Request and response schemas for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from uuid import UUID


# ==================== Job Schemas ====================

class JobCreate(BaseModel):
    """Schema for creating a new job."""
    title: str = Field(..., min_length=1, max_length=255)
    company: Optional[str] = None
    description: str = Field(..., min_length=10)
    skills: Optional[List[str]] = []


class JobResponse(BaseModel):
    """Schema for job response."""
    id: str
    title: str
    company: Optional[str]
    description: str
    skills: List[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class JobListResponse(BaseModel):
    """Schema for job list response."""
    count: int
    jobs: List[JobResponse]


# ==================== Resume Schemas ====================

class ResumeCreate(BaseModel):
    """Schema for creating a new resume."""
    name: str = Field(..., min_length=1, max_length=255)
    email: Optional[str] = None
    content: str = Field(..., min_length=10)
    skills: Optional[List[str]] = []


class ResumeResponse(BaseModel):
    """Schema for resume response."""
    id: str
    name: str
    email: Optional[str]
    content: str
    skills: List[str]
    created_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ResumeListResponse(BaseModel):
    """Schema for resume list response."""
    count: int
    resumes: List[ResumeResponse]


# ==================== Matching Schemas ====================

class ResumeInput(BaseModel):
    """Schema for resume input in manual match."""
    name: str = Field(..., min_length=1)
    content: str = Field(..., min_length=10)
    skills: Optional[List[str]] = []


class ManualMatchRequest(BaseModel):
    """Schema for manual match request."""
    job_description: str = Field(..., min_length=10)
    job_skills: Optional[List[str]] = []
    resumes: List[ResumeInput] = Field(..., min_length=1)


class MatchClassification(BaseModel):
    """Schema for match classification."""
    level: str  # high, medium, low
    label: str  # Strong Fit, Partial Fit, Needs Development
    color: str  # #22c55e, #f59e0b, #ef4444
    recommendations: List[str]


class SkillGapInfo(BaseModel):
    """Schema for skill gap information."""
    coverage: float
    critical_missing: List[str]
    recommendations: List[str]


class MatchResult(BaseModel):
    """Schema for a single match result."""
    name: str
    score: float
    content_similarity: float
    skill_similarity: float
    classification: MatchClassification
    matched_skills: List[str]
    missing_skills: List[str]
    resume_extract: str
    skill_gap: SkillGapInfo
    explanation: Optional[str] = None


class ManualMatchResponse(BaseModel):
    """Schema for manual match response."""
    job_skills_detected: List[str]
    total_resumes: int
    results: List[MatchResult]
    llm_enabled: bool = False


# ==================== Skill Extraction Schemas ====================

class SkillExtractionRequest(BaseModel):
    """Schema for skill extraction request."""
    text: str = Field(..., min_length=1)


class SkillExtractionResponse(BaseModel):
    """Schema for skill extraction response."""
    skills: List[str]
    count: int


# ==================== Task Schemas ====================

class TaskResponse(BaseModel):
    """Schema for background task response."""
    id: str
    task_type: str
    status: str
    progress: Optional[str]
    progress_percent: str
    result: Optional[dict]
    error: Optional[str]
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class TaskStartResponse(BaseModel):
    """Schema for task start response."""
    task_id: str
    status: str
    message: str


# ==================== Health Check Schemas ====================

class HealthResponse(BaseModel):
    """Schema for health check response."""
    status: str
    version: str
    jobs_count: int
    resumes_count: int
    database: str
    llm_available: bool


# ==================== LLM Schemas ====================

class LLMConfigRequest(BaseModel):
    """Schema for LLM configuration request."""
    api_url: Optional[str] = None
    model: Optional[str] = None
    enabled: Optional[bool] = None


class LLMStatusResponse(BaseModel):
    """Schema for LLM status response."""
    enabled: bool
    available: bool
    api_url: str
    model: str


# ==================== File Upload Response ====================

class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    success: bool
    filename: str
    text: str
    skills: List[str]
    char_count: int


# ==================== Error Schema ====================

class ErrorResponse(BaseModel):
    """Schema for error response."""
    error: str
    detail: Optional[str] = None
