"""
LLM Service using LM Studio (local) or any OpenAI-compatible API
Enhanced with email generation, recommendations, and intelligent actions.
"""

import json
import urllib.request
import urllib.error
from typing import List, Optional
import logging

from core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    LLM service for AI-powered features.
    
    What it does (beyond just search):
    - Explains WHY a candidate matches
    - Writes personalized outreach emails
    - Generates interview questions
    - Provides career recommendations
    """
    
    _instance: Optional["LLMService"] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.api_url = f"{settings.LLM_API_URL}/chat/completions"
            self.models_url = f"{settings.LLM_API_URL}/models"
            self.model = settings.LLM_MODEL
            self.enabled = settings.LLM_ENABLED
            self._initialized = True
    
    def is_available(self) -> bool:
        """Check if LLM service is reachable."""
        if not self.enabled:
            return False
        try:
            req = urllib.request.Request(self.models_url, method="GET")
            with urllib.request.urlopen(req, timeout=3) as res:
                return res.status == 200
        except Exception:
            return False
    
    def _call(self, system_prompt: str, user_prompt: str, max_tokens: int = 600) -> str:
        """Make a chat completion request."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.7,
            "max_tokens": max_tokens,
            "stream": False,
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(self.api_url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        
        try:
            with urllib.request.urlopen(req, timeout=90) as res:
                body = json.loads(res.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"].strip()
        except urllib.error.HTTPError as e:
            error_msg = f"LLM HTTP error: {e.read().decode()}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise RuntimeError(f"LLM call failed: {e}")
    
    def generate_match_explanation(
        self,
        job_description: str,
        resume_content: str,
        resume_name: str,
        score: float,
        matched_skills: List[str],
        missing_skills: List[str],
        content_similarity: float = 0,
        skill_similarity: float = 0
    ) -> str:
        """
        Generate a human-readable explanation of why a candidate matches.
        
        This is the "Hybrid Intelligence" - the LLM doesn't just search,
        it EXPLAINS the match results in natural language.
        """
        if not self.enabled or not self.is_available():
            return self._generate_fallback_explanation(
                score, matched_skills, missing_skills
            )
        
        system_prompt = """You are an expert technical recruiter and career advisor.
Analyze the match between this candidate and job. Be honest, specific, and actionable.
Format your response in clear sections with bullet points."""

        user_prompt = f"""## JOB DESCRIPTION:
{job_description[:1000]}

## CANDIDATE: {resume_name}
{resume_content[:1000]}

## MATCH ANALYSIS:
- Overall Score: {score:.0%}
- Content Similarity: {content_similarity:.0%}
- Skill Match: {skill_similarity:.0%}
- Matched Skills: {', '.join(matched_skills) or 'None identified'}
- Missing Skills: {', '.join(missing_skills) or 'None'}

Please provide:
1. **Match Verdict**: Is this a good fit? Why?
2. **Key Strengths**: What makes this candidate stand out?
3. **Skill Gaps**: What's missing and how critical is it?
4. **Next Steps**: Interview questions or development recommendations
5. **Hiring Recommendation**: Proceed, Consider, or Pass?"""

        try:
            return self._call(system_prompt, user_prompt, max_tokens=800)
        except Exception as e:
            logger.warning(f"LLM explanation failed, using fallback: {e}")
            return self._generate_fallback_explanation(score, matched_skills, missing_skills)
    
    def generate_outreach_email(
        self,
        job_title: str,
        company_name: str,
        candidate_name: str,
        matched_skills: List[str],
        personalization_notes: str = ""
    ) -> str:
        """
        Generate a personalized outreach email for a candidate.
        
        This is where the system "Acts" instead of just "Searches".
        """
        if not self.enabled or not self.is_available():
            return self._generate_fallback_email(job_title, company_name, candidate_name)
        
        system_prompt = """You are a professional recruiter writing outreach emails.
Write engaging, personalized emails that highlight relevant skills.
Keep emails concise (under 200 words) and include a clear call to action."""

        user_prompt = f"""Write a recruiting outreach email:

**Position**: {job_title}
**Company**: {company_name}
**Candidate**: {candidate_name}
**Relevant Skills**: {', '.join(matched_skills)}
**Notes**: {personalization_notes or 'None'}

Write a professional, warm email inviting them to discuss the opportunity."""

        try:
            return self._call(system_prompt, user_prompt, max_tokens=400)
        except Exception as e:
            logger.warning(f"LLM email generation failed: {e}")
            return self._generate_fallback_email(job_title, company_name, candidate_name)
    
    def generate_interview_questions(
        self,
        job_title: str,
        required_skills: List[str],
        candidate_skills: List[str],
        missing_skills: List[str]
    ) -> str:
        """Generate targeted interview questions based on the match analysis."""
        if not self.enabled or not self.is_available():
            return "LLM unavailable. Consider asking about: " + ", ".join(required_skills[:5])
        
        system_prompt = """You are a technical interviewer.
Generate specific, skill-focused interview questions.
Include both technical and behavioral questions."""

        user_prompt = f"""Generate interview questions for:

**Position**: {job_title}
**Required Skills**: {', '.join(required_skills)}
**Candidate Has**: {', '.join(candidate_skills)}
**Gaps to Probe**: {', '.join(missing_skills)}

Provide 5-7 targeted questions that assess both strengths and gaps."""

        try:
            return self._call(system_prompt, user_prompt, max_tokens=500)
        except Exception as e:
            logger.warning(f"LLM interview questions failed: {e}")
            return "LLM unavailable. Consider asking about: " + ", ".join(required_skills[:5])
    
    def generate_career_recommendations(
        self,
        current_skills: List[str],
        target_job: str,
        missing_skills: List[str]
    ) -> str:
        """Generate career development recommendations for a candidate."""
        if not self.enabled or not self.is_available():
            return f"Focus on learning: {', '.join(missing_skills[:5])}"
        
        system_prompt = """You are a career advisor and mentor.
Provide actionable, specific recommendations for skill development.
Include learning resources and timeline estimates."""

        user_prompt = f"""Provide career recommendations:

**Target Role**: {target_job}
**Current Skills**: {', '.join(current_skills)}
**Skills to Develop**: {', '.join(missing_skills)}

Recommend:
1. Priority skills to learn (and why)
2. Specific courses/resources
3. Projects to build
4. Estimated timeline to become job-ready"""

        try:
            return self._call(system_prompt, user_prompt, max_tokens=600)
        except Exception as e:
            logger.warning(f"LLM career recommendations failed: {e}")
            return f"Focus on learning: {', '.join(missing_skills[:5])}"
    
    def _generate_fallback_explanation(
        self, score: float, matched_skills: List[str], missing_skills: List[str]
    ) -> str:
        """Generate a rule-based explanation when LLM is unavailable."""
        if score >= 0.7:
            verdict = "Strong Fit"
            recommendation = "Recommend proceeding to interview"
        elif score >= 0.4:
            verdict = "Partial Fit"
            recommendation = "Consider for interview with focus on skill gaps"
        else:
            verdict = "Weak Fit"
            recommendation = "May need more experience"
        
        explanation = f"""**Match Verdict**: {verdict} ({score:.0%} match)

**Matched Skills**: {', '.join(matched_skills) or 'None identified'}

**Missing Skills**: {', '.join(missing_skills) or 'None'}

**Recommendation**: {recommendation}

_Note: AI explanation unavailable. Enable LLM for detailed analysis._"""
        
        return explanation
    
    def _generate_fallback_email(
        self, job_title: str, company_name: str, candidate_name: str
    ) -> str:
        """Generate a template email when LLM is unavailable."""
        return f"""Subject: Exciting {job_title} Opportunity at {company_name}

Hi {candidate_name},

I came across your profile and was impressed by your background. We have an exciting {job_title} position at {company_name} that I think could be a great fit.

Would you be open to a quick call to discuss this opportunity?

Best regards,
[Your Name]

_Note: This is a template. Enable LLM for personalized emails._"""


# Global instance
_llm_service: Optional[LLMService] = None


def get_llm_service() -> LLMService:
    """Get the global LLM service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


def configure_llm(api_url: str = None, model: str = None, enabled: bool = None):
    """Configure the LLM service."""
    llm = get_llm_service()
    if api_url:
        llm.api_url = f"{api_url.rstrip('/')}/chat/completions"
        llm.models_url = f"{api_url.rstrip('/')}/models"
    if model:
        llm.model = model
    if enabled is not None:
        llm.enabled = enabled
    return llm
