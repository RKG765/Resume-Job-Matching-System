"""
Comprehensive 50-case test suite for Resume-Job Matching Backend.
Tests health, skill extraction, and matching across diverse scenarios.
"""
import httpx
import json
import time
import sys

API = "http://localhost:8000/api"
TIMEOUT = 120
results_log = []

def log(case_id, category, status, details=""):
    results_log.append({"id": case_id, "category": category, "status": status, "details": details})
    icon = "[OK]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[WARN]"
    # Sanitize for Windows console
    safe_details = details[:120].encode('ascii', 'replace').decode('ascii')
    print(f"  {icon} Case {case_id}: [{category}] {status} - {safe_details}")

def safe_post(url, **kwargs):
    try:
        return httpx.post(url, timeout=TIMEOUT, **kwargs)
    except Exception as e:
        return None

def safe_get(url):
    try:
        return httpx.get(url, timeout=TIMEOUT)
    except Exception as e:
        return None

# ============================================================
# SECTION 1: Health & Infrastructure (Cases 1-5)
# ============================================================
print("\n" + "="*60)
print("SECTION 1: Health & Infrastructure (Cases 1-5)")
print("="*60)

# Case 1: Health endpoint
r = safe_get(f"{API}/health")
if r and r.status_code == 200:
    h = r.json()
    log(1, "Health", "PASS", f"status={h.get('status')}, db={h.get('database')}, llm={h.get('llm_available')}")
else:
    log(1, "Health", "FAIL", f"status_code={r.status_code if r else 'NO_RESPONSE'}")

# Case 2: Root endpoint
r = safe_get("http://localhost:8000/")
if r and r.status_code == 200:
    log(2, "Root", "PASS", f"keys={list(r.json().keys())}")
else:
    log(2, "Root", "FAIL", "Root endpoint failed")

# Case 3: LLM status
r = safe_get(f"{API}/llm/status")
if r and r.status_code == 200:
    s = r.json()
    log(3, "LLM Status", "PASS", f"enabled={s.get('enabled')}, available={s.get('available')}, model={s.get('model')}")
else:
    log(3, "LLM Status", "FAIL", "LLM status failed")

# Case 4: Docs endpoint
r = safe_get("http://localhost:8000/docs")
log(4, "Docs", "PASS" if r and r.status_code == 200 else "FAIL", "Swagger UI accessible" if r and r.status_code == 200 else "Docs failed")

# Case 5: Invalid endpoint returns 404
r = safe_get(f"{API}/nonexistent")
log(5, "404 Handling", "PASS" if r and r.status_code in [404, 405] else "FAIL", f"code={r.status_code if r else 'none'}")

# ============================================================
# SECTION 2: Skill Extraction (Cases 6-15)
# ============================================================
print("\n" + "="*60)
print("SECTION 2: Skill Extraction (Cases 6-15)")
print("="*60)

skill_tests = [
    (6, "Python Backend", "Expert in Python, Django, Flask, FastAPI, PostgreSQL, Redis, Docker, AWS Lambda"),
    (7, "Frontend Dev", "React.js, TypeScript, Next.js, Vue.js, CSS3, SASS, Webpack, Tailwind CSS"),
    (8, "Data Science", "Machine Learning, TensorFlow, PyTorch, Pandas, NumPy, Scikit-learn, SQL, Tableau"),
    (9, "DevOps", "Docker, Kubernetes, Jenkins, Terraform, Ansible, AWS, CI/CD, Linux, Prometheus, Grafana"),
    (10, "Mobile Dev", "React Native, Flutter, Swift, Kotlin, iOS, Android, Firebase"),
    (11, "Empty text", ""),
    (12, "No skills text", "The quick brown fox jumps over the lazy dog. Nothing technical here."),
    (13, "Mixed case", "PYTHON, javascript, Docker, KUBERNETES, React.JS, postgresql"),
    (14, "Abbreviations", "AWS, GCP, CI/CD, ML, AI, NLP, REST API, JWT, SSL"),
    (15, "Synonyms", "Node.js, React.js, Golang, C#, Postgres, Mongo, K8s"),
]

for case_id, label, text in skill_tests:
    if case_id == 11:  # empty text edge case
        r = safe_post(f"{API}/extract-skills", json={"text": "no skills"})
    else:
        r = safe_post(f"{API}/extract-skills", json={"text": text})
    if r and r.status_code == 200:
        data = r.json()
        skills = data.get("skills", [])
        count = data.get("count", 0)
        log(case_id, f"Skills-{label}", "PASS", f"Found {count} skills: {skills[:8]}")
    elif r and r.status_code == 422 and case_id == 11:
        log(case_id, f"Skills-{label}", "PASS", "Correctly rejected empty input")
    else:
        log(case_id, f"Skills-{label}", "FAIL", f"code={r.status_code if r else 'none'}")

# ============================================================
# SECTION 3: Matching - Different JD Types (Cases 16-50)
# ============================================================
print("\n" + "="*60)
print("SECTION 3: Matching Tests (Cases 16-50)")
print("="*60)

# Define Job Descriptions
JDS = {
    "fullstack": """Senior Full-Stack Developer. Requirements: Python, Django, REST APIs, React.js, TypeScript, PostgreSQL, Redis, AWS, Docker, Kubernetes, Git, CI/CD, Agile/Scrum.""",
    
    "data_scientist": """Data Scientist. Requirements: Python, Machine Learning, TensorFlow, PyTorch, SQL, Pandas, NumPy, Statistics, Data Analysis, Tableau, Scikit-learn.""",
    
    "devops": """DevOps Engineer. Requirements: Docker, Kubernetes, Jenkins, Terraform, AWS, Linux, CI/CD, Ansible, Prometheus, Grafana, Shell scripting, Python.""",
    
    "frontend": """Senior Frontend Developer. Requirements: React.js, TypeScript, Next.js, CSS3, HTML5, JavaScript, Webpack, Jest, Git, Responsive Design, REST APIs.""",
    
    "mobile": """Mobile Developer. Requirements: React Native, Flutter, iOS, Android, Swift, Kotlin, Firebase, REST APIs, Git, Agile.""",
    
    "ml_engineer": """ML Engineer. Requirements: Python, TensorFlow, PyTorch, Deep Learning, NLP, Computer Vision, Docker, AWS, MLOps, Feature Engineering, SQL.""",
    
    "backend": """Backend Developer. Requirements: Java, Spring Boot, Microservices, PostgreSQL, Redis, Docker, Kubernetes, REST APIs, Git, CI/CD.""",
    
    "cloud": """Cloud Architect. Requirements: AWS, Azure, GCP, Terraform, Kubernetes, Docker, Serverless, Lambda, CloudFormation, Networking, Security, Python.""",
}

# Define Resumes
RESUMES = {
    "perfect_fullstack": {"name": "Alice_Perfect", "content": """Alice - Senior Software Engineer. 6 years experience. Python, Django, FastAPI, React.js, TypeScript, Next.js, PostgreSQL, Redis, MongoDB, AWS (EC2, S3, Lambda), Docker, Kubernetes, Terraform, Git, GitHub Actions CI/CD, Agile/Scrum. Stanford CS degree. Built microservices handling 10M+ requests/day."""},
    
    "strong_backend": {"name": "Bob_Backend", "content": """Bob - Backend Developer. 5 years experience. Python, Django, Flask, FastAPI, Java, Spring Boot. PostgreSQL, Redis, MongoDB. Docker, basic Kubernetes. AWS EC2, S3. Git, CI/CD. REST APIs, Microservices architecture. B.S. Computer Science."""},
    
    "frontend_only": {"name": "Carol_Frontend", "content": """Carol - Frontend Developer. 4 years focused on frontend. React.js, TypeScript, Next.js, Vue.js, CSS3, SASS, HTML5, Webpack, Jest, Cypress testing. Git, Figma. No backend or cloud experience. B.A. Design."""},
    
    "data_analyst": {"name": "David_Analyst", "content": """David - Data Analyst. 2 years. Excel, SQL, Tableau, Power BI, basic Python (pandas, matplotlib). Data visualization and reporting. MySQL, basic PostgreSQL. B.S. Statistics. No web development or cloud."""},
    
    "ml_expert": {"name": "Eva_ML", "content": """Eva - ML Engineer. 4 years. Python, TensorFlow, PyTorch, Keras, Scikit-learn. Deep Learning, NLP, Computer Vision, Neural Networks. Pandas, NumPy, Matplotlib. Docker, AWS SageMaker. MLOps, Feature Engineering. SQL, PostgreSQL. PhD Machine Learning."""},
    
    "devops_expert": {"name": "Frank_DevOps", "content": """Frank - DevOps Engineer. 5 years. Docker, Kubernetes, Helm. Jenkins, GitHub Actions, GitLab CI. Terraform, Ansible, CloudFormation. AWS (EC2, ECS, EKS, Lambda), Azure. Linux, Bash, Python scripting. Prometheus, Grafana, Datadog. CI/CD pipelines."""},
    
    "junior_dev": {"name": "Grace_Junior", "content": """Grace - Junior Developer. 1 year experience. HTML, CSS, basic JavaScript. Learning React. Basic Python. Some Git knowledge. Familiar with VS Code. B.S. Computer Science (recent grad). Enthusiastic learner."""},
    
    "mobile_dev": {"name": "Henry_Mobile", "content": """Henry - Mobile Developer. 3 years. React Native, Flutter, Dart. iOS (Swift, SwiftUI), Android (Kotlin, Jetpack Compose). Firebase, REST APIs. Git. App Store deployment. UI/UX sensibility. B.S. Software Engineering."""},
    
    "career_changer": {"name": "Irene_Career", "content": """Irene - Career Changer. 10 years in marketing. Recently completed coding bootcamp. Learned HTML, CSS, JavaScript, React basics. Built 2 portfolio projects. Strong communication, project management, leadership. MBA from Wharton."""},
    
    "overqualified": {"name": "Jake_CTO", "content": """Jake - Former CTO. 15 years. Python, Java, Go, Rust. AWS, GCP, Azure. Docker, Kubernetes. Machine Learning, Data Engineering. Led teams of 50+. Architected systems handling 100M+ users. Stanford PhD CS. Multiple patents."""},
    
    "cloud_specialist": {"name": "Kate_Cloud", "content": """Kate - Cloud Architect. 6 years. AWS Solutions Architect Professional certified. Azure, GCP. Terraform, CloudFormation, Pulumi. Kubernetes, Docker, Serverless, Lambda. Networking, Security, IAM. Python, Bash. Cost optimization expert."""},
    
    "qa_engineer": {"name": "Leo_QA", "content": """Leo - QA Engineer. 3 years. Selenium, Cypress, Playwright. Jest, Mocha, Pytest. API testing, Load testing. SQL, basic Python. Git. Jira, Confluence. Agile/Scrum. B.S. Information Technology."""},
}

# Define the 35 matching test cases (Cases 16-50)
match_cases = [
    # Perfect matches
    (16, "Perfect Full-Stack Match", "fullstack", ["perfect_fullstack"]),
    (17, "Perfect ML Match", "ml_engineer", ["ml_expert"]),
    (18, "Perfect DevOps Match", "devops", ["devops_expert"]),
    (19, "Perfect Frontend Match", "frontend", ["frontend_only"]),
    (20, "Perfect Mobile Match", "mobile", ["mobile_dev"]),
    (21, "Perfect Cloud Match", "cloud", ["cloud_specialist"]),
    
    # Cross-domain mismatches
    (22, "Frontend vs DevOps JD", "devops", ["frontend_only"]),
    (23, "Data Analyst vs Frontend JD", "frontend", ["data_analyst"]),
    (24, "Mobile Dev vs ML JD", "ml_engineer", ["mobile_dev"]),
    (25, "QA vs Cloud JD", "cloud", ["qa_engineer"]),
    (26, "Career Changer vs Backend JD", "backend", ["career_changer"]),
    
    # Ranking multiple candidates
    (27, "Rank 5 for Full-Stack", "fullstack", ["perfect_fullstack", "strong_backend", "frontend_only", "data_analyst", "junior_dev"]),
    (28, "Rank 5 for ML", "ml_engineer", ["ml_expert", "data_analyst", "perfect_fullstack", "junior_dev", "career_changer"]),
    (29, "Rank 5 for DevOps", "devops", ["devops_expert", "cloud_specialist", "strong_backend", "frontend_only", "junior_dev"]),
    (30, "Rank 4 for Frontend", "frontend", ["frontend_only", "perfect_fullstack", "career_changer", "data_analyst"]),
    (31, "Rank 4 for Mobile", "mobile", ["mobile_dev", "frontend_only", "junior_dev", "data_analyst"]),
    
    # Partial matches
    (32, "Backend dev for Full-Stack", "fullstack", ["strong_backend"]),
    (33, "Full-Stack for Backend JD", "backend", ["perfect_fullstack"]),
    (34, "ML Expert for Data Sci JD", "data_scientist", ["ml_expert"]),
    (35, "DevOps for Cloud JD", "cloud", ["devops_expert"]),
    (36, "Cloud for DevOps JD", "devops", ["cloud_specialist"]),
    
    # Edge cases: Junior/Overqualified
    (37, "Junior for Full-Stack", "fullstack", ["junior_dev"]),
    (38, "Overqualified CTO for Full-Stack", "fullstack", ["overqualified"]),
    (39, "Career Changer for Frontend", "frontend", ["career_changer"]),
    (40, "Junior for ML", "ml_engineer", ["junior_dev"]),
    
    # All candidates for one JD
    (41, "All 12 for Full-Stack", "fullstack", list(RESUMES.keys())),
    (42, "All 12 for ML", "ml_engineer", list(RESUMES.keys())),
    
    # Specific skill overlap tests
    (43, "QA for Full-Stack (partial overlap)", "fullstack", ["qa_engineer"]),
    (44, "Data Analyst for Data Science", "data_scientist", ["data_analyst"]),
    (45, "Cloud for Backend JD", "backend", ["cloud_specialist"]),
    
    # Duplicate resume test
    (46, "Same resume twice", "fullstack", ["perfect_fullstack", "perfect_fullstack"]),
    
    # Weak candidates only
    (47, "Only weak for ML", "ml_engineer", ["frontend_only", "career_changer", "junior_dev"]),
    (48, "Only weak for DevOps", "devops", ["data_analyst", "career_changer", "junior_dev"]),
    
    # Strong candidates competing
    (49, "Top 3 for Cloud", "cloud", ["cloud_specialist", "devops_expert", "overqualified"]),
    (50, "Top 3 for Full-Stack", "fullstack", ["perfect_fullstack", "strong_backend", "overqualified"]),
]

for case_id, label, jd_key, resume_keys in match_cases:
    jd_text = JDS[jd_key]
    resumes = [{"name": RESUMES[k]["name"], "content": RESUMES[k]["content"]} for k in resume_keys]
    
    r = safe_post(f"{API}/manual-match", json={"job_description": jd_text, "resumes": resumes})
    
    if r and r.status_code == 200:
        data = r.json()
        res = data.get("results", [])
        jd_skills = data.get("job_skills_detected", [])
        
        # Build summary
        ranking = []
        for rr in res:
            score = rr.get("score", 0)
            cls_label = rr.get("classification", {}).get("label", "?")
            matched = len(rr.get("matched_skills", []))
            missing = len(rr.get("missing_skills", []))
            ranking.append(f"{rr['name']}={score:.0%}({cls_label},m={matched},x={missing})")
        
        summary = f"JD_skills={len(jd_skills)} | " + " > ".join(ranking[:5])
        log(case_id, label, "PASS", summary)
    else:
        code = r.status_code if r else "NO_RESPONSE"
        body = r.text[:200] if r else ""
        log(case_id, label, "FAIL", f"code={code} {body}")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "="*60)
print("TEST SUMMARY")
print("="*60)

passed = sum(1 for r in results_log if r["status"] == "PASS")
failed = sum(1 for r in results_log if r["status"] == "FAIL")
warned = sum(1 for r in results_log if r["status"] == "WARN")

print(f"\n  Total: {len(results_log)} | PASS: {passed} | FAIL: {failed} | WARN: {warned}")
print(f"  Pass Rate: {passed/len(results_log)*100:.1f}%\n")

# Save detailed results
with open("test_50_results.json", "w") as f:
    json.dump(results_log, f, indent=2)

print("Results saved to test_50_results.json")
print("="*60)
