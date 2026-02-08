"""
FastAPI Routes
All API endpoints for the Resume-Job Matching System.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging
import io

from core.database import get_db
from core.config import settings
from api.schemas import (
    JobCreate, JobResponse, JobListResponse,
    ResumeCreate, ResumeResponse, ResumeListResponse,
    ManualMatchRequest, ManualMatchResponse, MatchResult,
    SkillExtractionRequest, SkillExtractionResponse,
    TaskResponse, TaskStartResponse,
    HealthResponse, LLMConfigRequest, LLMStatusResponse,
    FileUploadResponse, ErrorResponse
)
from services.db_service import DatabaseService
from services.matching_service import get_matching_service
from services.llm_service import get_llm_service, configure_llm
from classification.skill_gap import SkillGapAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter()


# ==================== Health Check ====================

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Check system health and component status."""
    llm = get_llm_service()
    
    try:
        db_service = DatabaseService(db)
        jobs_count = await db_service.count_jobs()
        resumes_count = await db_service.count_resumes()
    except Exception as e:
        logger.warning(f"Database count failed: {e}")
        jobs_count = -1
        resumes_count = -1
    
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        jobs_count=jobs_count,
        resumes_count=resumes_count,
        database="postgresql" if not settings.USE_SQLITE else "sqlite",
        llm_available=llm.is_available()
    )


# ==================== Job Endpoints ====================

@router.post("/jobs", response_model=JobResponse, tags=["Jobs"])
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    """Create a new job with automatic embedding generation."""
    db_service = DatabaseService(db)
    created_job = await db_service.create_job(
        title=job.title,
        company=job.company,
        description=job.description,
        skills=job.skills
    )
    return JobResponse(
        id=str(created_job.id),
        title=created_job.title,
        company=created_job.company,
        description=created_job.description[:500],
        skills=created_job.skills or [],
        created_at=created_job.created_at
    )


@router.get("/jobs", response_model=JobListResponse, tags=["Jobs"])
async def list_jobs(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all indexed jobs."""
    db_service = DatabaseService(db)
    jobs = await db_service.get_jobs(limit=limit, offset=offset)
    count = await db_service.count_jobs()
    
    return JobListResponse(
        count=count,
        jobs=[JobResponse(
            id=str(j.id),
            title=j.title,
            company=j.company,
            description=j.description[:500] if j.description else "",
            skills=j.skills or [],
            created_at=j.created_at
        ) for j in jobs]
    )


@router.get("/jobs/{job_id}", response_model=JobResponse, tags=["Jobs"])
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific job by ID."""
    db_service = DatabaseService(db)
    job = await db_service.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return JobResponse(
        id=str(job.id),
        title=job.title,
        company=job.company,
        description=job.description,
        skills=job.skills or [],
        created_at=job.created_at
    )


@router.delete("/jobs/{job_id}", tags=["Jobs"])
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a job."""
    db_service = DatabaseService(db)
    deleted = await db_service.delete_job(job_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"success": True, "message": "Job deleted"}


# ==================== Resume Endpoints ====================

@router.post("/resumes", response_model=ResumeResponse, tags=["Resumes"])
async def create_resume(resume: ResumeCreate, db: AsyncSession = Depends(get_db)):
    """Create a new resume with automatic embedding generation."""
    db_service = DatabaseService(db)
    created_resume = await db_service.create_resume(
        name=resume.name,
        email=resume.email,
        content=resume.content,
        skills=resume.skills
    )
    return ResumeResponse(
        id=str(created_resume.id),
        name=created_resume.name,
        email=created_resume.email,
        content=created_resume.content[:500],
        skills=created_resume.skills or [],
        created_at=created_resume.created_at
    )


@router.get("/resumes", response_model=ResumeListResponse, tags=["Resumes"])
async def list_resumes(
    limit: int = 100,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """List all indexed resumes."""
    db_service = DatabaseService(db)
    resumes = await db_service.get_resumes(limit=limit, offset=offset)
    count = await db_service.count_resumes()
    
    return ResumeListResponse(
        count=count,
        resumes=[ResumeResponse(
            id=str(r.id),
            name=r.name,
            email=r.email,
            content=r.content[:500] if r.content else "",
            skills=r.skills or [],
            created_at=r.created_at
        ) for r in resumes]
    )


@router.delete("/resumes/{resume_id}", tags=["Resumes"])
async def delete_resume(resume_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a resume."""
    db_service = DatabaseService(db)
    deleted = await db_service.delete_resume(resume_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Resume not found")
    
    return {"success": True, "message": "Resume deleted"}


# ==================== Matching Endpoints ====================

@router.post("/manual-match", response_model=ManualMatchResponse, tags=["Matching"])
async def manual_match(request: ManualMatchRequest):
    """
    Match multiple resumes against a job description.
    Uses BERT embeddings for semantic understanding.
    """
    matching_service = get_matching_service()
    llm = get_llm_service()
    skill_analyzer = SkillGapAnalyzer()
    
    # Extract job skills if not provided
    job_skills = request.job_skills or list(skill_analyzer.extract_skills(request.job_description))
    
    # Convert to dict format
    resumes = [{"name": r.name, "content": r.content, "skills": r.skills} for r in request.resumes]
    
    # Run matching
    results = matching_service.batch_match(
        job_description=request.job_description,
        resumes=resumes,
        job_skills=job_skills
    )
    
    # Generate LLM explanations for each result
    for result in results:
        explanation = llm.generate_match_explanation(
            job_description=request.job_description,
            resume_content=result.get("resume_extract", ""),
            resume_name=result.get("name", "Unknown"),
            score=result.get("score", 0),
            matched_skills=result.get("matched_skills", []),
            missing_skills=result.get("missing_skills", []),
            content_similarity=result.get("content_similarity", 0),
            skill_similarity=result.get("skill_similarity", 0)
        )
        result["explanation"] = explanation
    
    return ManualMatchResponse(
        job_skills_detected=job_skills,
        total_resumes=len(resumes),
        results=[MatchResult(**r) for r in results],
        llm_enabled=llm.enabled and llm.is_available()
    )


@router.post("/rank/{job_id}", tags=["Matching"])
async def rank_resumes_for_job(
    job_id: str,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """
    Rank all stored resumes against a specific job.
    Uses semantic search with pgvector.
    """
    from uuid import UUID
    db_service = DatabaseService(db)
    
    job = await db_service.get_job(UUID(job_id))
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Use vector similarity search
    similar_resumes = await db_service.find_similar_resumes(
        job.description,
        limit=limit
    )
    
    matching_service = get_matching_service()
    results = []
    
    for resume, similarity in similar_resumes:
        match_result = matching_service.match_resume_to_job(
            resume_content=resume.content,
            job_description=job.description,
            resume_skills=resume.skills,
            job_skills=job.skills
        )
        results.append({
            "resume_id": str(resume.id),
            "name": resume.name,
            "semantic_similarity": round(similarity, 4),
            **match_result
        })
    
    return {
        "job_id": job_id,
        "job_title": job.title,
        "total_resumes": len(results),
        "results": results
    }


# ==================== Skill Extraction ====================

@router.post("/extract-skills", response_model=SkillExtractionResponse, tags=["Skills"])
async def extract_skills(request: SkillExtractionRequest):
    """Extract skills from text using NLP patterns."""
    skill_analyzer = SkillGapAnalyzer()
    skills = list(skill_analyzer.extract_skills(request.text))
    
    return SkillExtractionResponse(
        skills=sorted(skills),
        count=len(skills)
    )


@router.post("/skill-gap", tags=["Skills"])
async def analyze_skill_gap(
    job_description: str = Form(...),
    resume_content: str = Form(...)
):
    """Analyze skill gaps between a resume and job."""
    skill_analyzer = SkillGapAnalyzer()
    analysis = skill_analyzer.analyze_gap(job_description, resume_content)
    return analysis


# ==================== File Upload ====================

def extract_pdf_text(content: bytes) -> str:
    """
    Extract text from PDF with multiple fallback methods.
    Tries PyPDF2 first, then pdfplumber for better extraction.
    """
    text = ""
    
    # Method 1: PyPDF2 (fast, works for most PDFs)
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        text = text.strip()
        
        # Check if we got meaningful text (not just binary garbage)
        if text and len(text) > 50 and not text.startswith('%PDF'):
            return clean_extracted_text(text)
    except Exception as e:
        logger.warning(f"PyPDF2 extraction failed: {e}")
    
    # Method 2: pdfplumber (better for complex layouts)
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        text = text.strip()
        
        if text and len(text) > 50:
            return clean_extracted_text(text)
    except ImportError:
        logger.info("pdfplumber not installed, skipping fallback")
    except Exception as e:
        logger.warning(f"pdfplumber extraction failed: {e}")
    
    # Method 3: Basic text extraction from raw bytes (last resort)
    try:
        # Try to find readable text in the PDF
        decoded = content.decode('utf-8', errors='ignore')
        # Extract text between stream markers (very basic)
        import re
        streams = re.findall(r'stream\s*(.*?)\s*endstream', decoded, re.DOTALL)
        if streams:
            text = ' '.join(streams[:5])  # First 5 streams only
            text = re.sub(r'[^\x20-\x7E\n]', ' ', text)  # Keep only printable
            text = ' '.join(text.split())
            if len(text) > 100:
                return text[:5000]  # Limit to first 5000 chars
    except Exception as e:
        logger.warning(f"Raw extraction failed: {e}")
    
    return text


def clean_extracted_text(text: str) -> str:
    """Clean extracted PDF text for better processing."""
    import re
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove common PDF artifacts
    text = re.sub(r'\x00', '', text)  # Null bytes
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f]', '', text)  # Control chars
    
    # Fix common encoding issues
    text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    # Restore paragraph breaks
    text = re.sub(r'([.!?])\s+([A-Z])', r'\1\n\n\2', text)
    
    return text.strip()


@router.post("/upload-file", response_model=FileUploadResponse, tags=["Upload"])
async def upload_file(file: UploadFile = File(...)):
    """Upload and parse a file (PDF or TXT) to extract text."""
    
    filename = file.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    try:
        content = await file.read()
        
        if file_ext == "pdf":
            text = extract_pdf_text(content)
            
            if not text or len(text) < 20:
                # Return error but don't fail completely
                return FileUploadResponse(
                    success=False,
                    filename=filename,
                    text="[PDF extraction failed - the file may be scanned/image-based. Please try a text-based PDF or TXT file.]",
                    skills=[],
                    char_count=0
                )
        elif file_ext in ["txt", "text"]:
            text = content.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Use PDF or TXT."
            )
        
        skill_analyzer = SkillGapAnalyzer()
        skills = list(skill_analyzer.extract_skills(text))
        
        return FileUploadResponse(
            success=True,
            filename=filename,
            text=text,
            skills=skills,
            char_count=len(text)
        )
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to parse file: {str(e)}")


@router.post("/upload-resume", tags=["Upload"])
async def upload_resume(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload a resume file and store it in the database."""
    
    filename = file.filename or "unknown"
    file_ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    
    try:
        content = await file.read()
        
        if file_ext == "pdf":
            text = extract_pdf_text(content)
            if not text or len(text) < 20:
                raise HTTPException(
                    status_code=400,
                    detail="Could not extract text from PDF. Try a text-based PDF or TXT file."
                )
        elif file_ext in ["txt", "text"]:
            text = content.decode("utf-8", errors="ignore")
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}"
            )
        
        candidate_name = name or filename.rsplit(".", 1)[0]
        
        db_service = DatabaseService(db)
        resume = await db_service.create_resume(
            name=candidate_name,
            content=text,
            filename=filename
        )
        
        return {
            "success": True,
            "resume_id": str(resume.id),
            "name": resume.name,
            "skills": resume.skills,
            "char_count": len(text)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Resume upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process resume: {str(e)}")


# ==================== LLM Endpoints ====================

@router.get("/llm/status", response_model=LLMStatusResponse, tags=["LLM"])
async def llm_status():
    """Check LLM service status."""
    llm = get_llm_service()
    return LLMStatusResponse(
        enabled=llm.enabled,
        available=llm.is_available(),
        api_url=llm.api_url,
        model=llm.model
    )


@router.post("/llm/configure", response_model=LLMStatusResponse, tags=["LLM"])
async def configure_llm_endpoint(config: LLMConfigRequest):
    """Configure the LLM service."""
    llm = configure_llm(
        api_url=config.api_url,
        model=config.model,
        enabled=config.enabled
    )
    return LLMStatusResponse(
        enabled=llm.enabled,
        available=llm.is_available(),
        api_url=llm.api_url,
        model=llm.model
    )


@router.post("/llm/generate-email", tags=["LLM"])
async def generate_outreach_email(
    job_title: str = Form(...),
    company_name: str = Form(...),
    candidate_name: str = Form(...),
    matched_skills: str = Form(""),
    notes: str = Form("")
):
    """Generate a personalized outreach email for a candidate."""
    llm = get_llm_service()
    skills_list = [s.strip() for s in matched_skills.split(",") if s.strip()]
    
    email = llm.generate_outreach_email(
        job_title=job_title,
        company_name=company_name,
        candidate_name=candidate_name,
        matched_skills=skills_list,
        personalization_notes=notes
    )
    
    return {"email": email}


# ==================== Background Tasks ====================

@router.post("/tasks/seed-sample-data", response_model=TaskStartResponse, tags=["Tasks"])
async def seed_sample_data(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Seed the database with sample jobs and resumes.
    Runs in background (async) - doesn't block the request.
    """
    from uuid import uuid4
    task_id = str(uuid4())
    
    async def _seed_data():
        db_service = DatabaseService(db)
        
        # Sample jobs
        sample_jobs = [
            {
                "title": "Senior Python Developer",
                "company": "Tech Corp",
                "description": "Looking for a Senior Python Developer with Django, Flask, AWS, Docker experience."
            },
            {
                "title": "Data Scientist",
                "company": "Analytics Inc",
                "description": "Join our data science team. Required: Python, TensorFlow, PyTorch, SQL, Machine Learning."
            },
            {
                "title": "Frontend Developer",
                "company": "WebStart",
                "description": "Build amazing UIs with React, TypeScript, CSS3, and modern frontend technologies."
            }
        ]
        
        for job in sample_jobs:
            await db_service.create_job(**job)
        
        logger.info(f"Seeded {len(sample_jobs)} sample jobs")
    
    background_tasks.add_task(_seed_data)
    
    return TaskStartResponse(
        task_id=task_id,
        status="started",
        message="Seeding sample data in background"
    )
