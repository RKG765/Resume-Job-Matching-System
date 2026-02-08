"""
Matching Service
Combines BERT embeddings with skill matching for resume-job matching.
"""

from typing import List, Dict, Optional
import logging

from services.embedding_service import get_embedding_service
from classification.skill_gap import SkillGapAnalyzer
from classification.classifier import classify_match

logger = logging.getLogger(__name__)


class MatchingService:
    """
    Resume-Job matching service using BERT embeddings.
    
    Combines:
    - Semantic similarity (BERT): Understands meaning, not just words
    - Skill matching (Jaccard): Exact skill overlap
    - Weighted scoring: (Content × 0.4) + (Skills × 0.6)
    """
    
    def __init__(self):
        self.embedding_service = get_embedding_service()
        self.skill_analyzer = SkillGapAnalyzer()
    
    def match_resume_to_job(
        self,
        resume_content: str,
        job_description: str,
        resume_skills: Optional[List[str]] = None,
        job_skills: Optional[List[str]] = None
    ) -> Dict:
        """
        Match a single resume to a job description.
        
        Args:
            resume_content: Resume text
            job_description: Job description text
            resume_skills: Pre-extracted resume skills (optional)
            job_skills: Pre-extracted job skills (optional)
            
        Returns:
            Match result with scores and skill analysis
        """
        # Extract skills if not provided
        if job_skills is None:
            job_skills = list(self.skill_analyzer.extract_skills(job_description))
        if resume_skills is None:
            resume_skills = list(self.skill_analyzer.extract_skills(resume_content))
        
        # Compute BERT semantic similarity
        content_similarity = self.embedding_service.similarity(
            job_description, 
            resume_content
        )
        
        # Compute skill overlap (Jaccard-like)
        job_skills_set = set(s.lower() for s in job_skills)
        resume_skills_set = set(s.lower() for s in resume_skills)
        
        if job_skills_set:
            skill_overlap = len(job_skills_set & resume_skills_set) / len(job_skills_set)
        else:
            skill_overlap = content_similarity  # Fallback to content similarity
        
        # Weighted final score
        # Skills weighted higher (0.6) because they're explicit requirements
        final_score = (0.4 * content_similarity) + (0.6 * skill_overlap)
        
        # Calculate matched and missing skills
        matched_skills = list(job_skills_set & resume_skills_set)
        missing_skills = list(job_skills_set - resume_skills_set)
        
        # Classify match
        classification = classify_match(final_score, matched_skills, missing_skills)
        
        # Get detailed skill gap analysis
        skill_gap = self.skill_analyzer.analyze_gap(
            job_description, resume_content,
            list(job_skills_set), list(resume_skills_set)
        )
        
        return {
            "score": round(final_score, 4),
            "content_similarity": round(content_similarity, 4),
            "skill_similarity": round(skill_overlap, 4),
            "classification": classification,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "skill_gap": {
                "coverage": skill_gap["coverage_percentage"],
                "critical_missing": skill_gap["critical_missing"],
                "recommendations": skill_gap["recommendations"]
            }
        }
    
    def batch_match(
        self,
        job_description: str,
        resumes: List[Dict],
        job_skills: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Match multiple resumes to a job description.
        
        Args:
            job_description: Job description text
            resumes: List of resume dicts with 'name', 'content', optionally 'skills'
            job_skills: Pre-extracted job skills (optional)
            
        Returns:
            Sorted list of match results (highest score first)
        """
        # Extract job skills once
        if job_skills is None:
            job_skills = list(self.skill_analyzer.extract_skills(job_description))
        
        results = []
        
        for resume in resumes:
            name = resume.get("name", "Unknown")
            content = resume.get("content", "")
            resume_skills = resume.get("skills", None)
            
            if not content:
                continue
            
            match_result = self.match_resume_to_job(
                resume_content=content,
                job_description=job_description,
                resume_skills=resume_skills,
                job_skills=job_skills
            )
            
            results.append({
                "name": name,
                "resume_extract": content[:2000],
                "resume_full": content,
                **match_result
            })
        
        # Sort by score (descending)
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results


# Global instance
_matching_service: Optional[MatchingService] = None


def get_matching_service() -> MatchingService:
    """Get the global matching service instance."""
    global _matching_service
    if _matching_service is None:
        _matching_service = MatchingService()
    return _matching_service
