"""End-to-end test of the Resume-Job Matching API."""
import httpx
import json

API = "http://localhost:8000/api"

# 1. Health check
health = httpx.get(f"{API}/health", timeout=10).json()
print("=== HEALTH CHECK ===")
print(f"  Status: {health.get('status')}")
print(f"  Embedding: {health.get('embedding_model')}")
print(f"  LLM: {health.get('llm_available')}")

# 2. Job Description
jd_text = """Senior Full-Stack Developer

We are looking for a Senior Full-Stack Developer with 5+ years of experience.

Requirements:
- Strong proficiency in Python, Django, and REST APIs
- Experience with React.js, TypeScript, and modern frontend frameworks
- Database expertise with PostgreSQL and Redis
- Cloud deployment on AWS (EC2, S3, Lambda)
- Docker and Kubernetes for containerization
- Git version control and CI/CD pipelines
- Strong problem-solving and communication skills
- Experience with Agile/Scrum methodology"""

# 3. Skill extraction test
skills_resp = httpx.post(f"{API}/extract-skills", json={"text": jd_text}, timeout=10).json()
skills = skills_resp.get("skills", [])
print(f"\n=== JD SKILL EXTRACTION ({len(skills)} skills) ===")
print(f"  {skills}")

# 4. Resumes: Strong, Good, Partial, Weak
resumes = [
    {
        "name": "Alice_Chen",
        "content": """Alice Chen - Senior Software Engineer
5+ years building web applications. Expert in Python, Django REST Framework, and FastAPI.
Frontend: React.js, TypeScript, Next.js, Tailwind CSS.
Databases: PostgreSQL, Redis, MongoDB.
Cloud: AWS (EC2, S3, Lambda, CloudFront), Docker, Kubernetes, Terraform.
Tools: Git, GitHub Actions CI/CD, Jira, Agile/Scrum.
Education: B.S. Computer Science, Stanford University.
Projects: Built microservices platform handling 10M+ requests/day."""
    },
    {
        "name": "Bob_Martinez",
        "content": """Bob Martinez - Full Stack Developer
3 years of experience in web development.
Backend: Python, Flask, basic Django. Built REST APIs for e-commerce platform.
Frontend: React, JavaScript (learning TypeScript).
Database: PostgreSQL, some MySQL experience.
Deployment: Docker, basic AWS EC2. Familiar with Git.
Education: B.S. Information Technology.
Projects: E-commerce platform with payment integration."""
    },
    {
        "name": "Carol_Johnson",
        "content": """Carol Johnson - Frontend Developer
4 years focused on frontend development.
Expert in React.js, TypeScript, Next.js, Vue.js, CSS/SASS.
Some backend experience with Node.js and Express.
Database: MongoDB, Firebase.
Tools: Git, Figma, Webpack, Jest testing.
Education: B.A. Design + self-taught programming.
No cloud or DevOps experience."""
    },
    {
        "name": "David_Kim",
        "content": """David Kim - Data Analyst
2 years as a data analyst.
Skills: Excel, SQL, Tableau, Power BI, basic Python (pandas, matplotlib).
Experience with data visualization and reporting.
Database: MySQL, basic PostgreSQL queries.
Education: B.S. Statistics.
No web development or cloud experience."""
    }
]

# 5. Run matching
print("\n=== RUNNING MATCH (4 resumes) ===")
match_resp = httpx.post(f"{API}/manual-match", json={
    "job_description": jd_text,
    "resumes": resumes
}, timeout=120).json()

jd_skills = match_resp.get("job_skills_detected", [])
print(f"  JD Skills: {jd_skills}")
print(f"  Total resumes: {match_resp.get('total_resumes')}")

# 6. Print results
for r in match_resp.get("results", []):
    score = r.get("score", 0)
    cls = r.get("classification", {})
    matched = r.get("matched_skills", [])
    missing = r.get("missing_skills", [])
    content_sim = r.get("content_similarity", 0)
    skill_sim = r.get("skill_similarity", 0)

    print(f"\n{'='*50}")
    print(f"  Candidate: {r['name']}")
    print(f"  Overall Score: {score:.0%}")
    print(f"  Classification: {cls.get('label','?')} ({cls.get('level','?')})")
    print(f"  Content Similarity (BERT): {content_sim:.0%}")
    print(f"  Skill Similarity (Jaccard): {skill_sim:.0%}")
    print(f"  Matched Skills ({len(matched)}): {matched}")
    print(f"  Missing Skills ({len(missing)}): {missing}")

    exp = r.get("explanation", "")
    if exp and len(exp) > 50:
        print(f"  AI Explanation (first 300 chars):")
        print(f"    {exp[:300]}...")
    
    gap = r.get("skill_gap", {})
    if gap:
        print(f"  Coverage: {gap.get('coverage', 0):.0f}%")
        recs = gap.get("recommendations", [])
        if recs:
            print(f"  Recommendations: {recs[:2]}")

print("\n=== TEST COMPLETE ===")
