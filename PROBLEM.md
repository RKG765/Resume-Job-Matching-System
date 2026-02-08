# Problem Statement

## Resume-Job Description Matching and Candidate Ranking System using Information Retrieval Techniques

---

## 1. Problem Definition

In modern recruitment, organizations receive hundreds or thousands of resumes for each job posting. Manual screening is:
- **Time-consuming**: Recruiters spend 6-8 seconds per resume on average
- **Inconsistent**: Human bias and fatigue affect decision quality
- **Inaccurate**: Keyword-based ATS systems miss semantically relevant candidates

**Challenge**: How can we build an intelligent Information Retrieval system that accurately matches candidate resumes to job descriptions, ranks them by relevance, and identifies skill gaps?

---

## 2. Proposed Solution

An end-to-end **Information Retrieval System** that:

1. **Represents Documents** using Sentence-BERT embeddings (384-dimensional dense vectors)
2. **Matches & Ranks** candidates using hybrid similarity scoring (semantic + skills)
3. **Classifies** candidates into Fit/Partial/Reject categories
4. **Analyzes Skill Gaps** with fuzzy matching and synonym resolution
5. **Computes Similarity** using cosine similarity on dense vector representations
6. **Explains Results** using integrated LLM for natural language summaries

---

## 3. Information Retrieval Concepts Applied

| IR Concept | Implementation in This Project |
|------------|-------------------------------|
| **Document Representation** | Sentence-BERT embeddings (384-dimensional dense vectors) |
| **Dense Retrieval** | Neural embeddings that capture semantic meaning |
| **Similarity Computation** | Cosine Similarity on embedding vectors |
| **Set-based Matching** | Jaccard Similarity for skill overlap |
| **Ranked Retrieval** | Weighted scoring: `(Semantic × 0.4) + (Skills × 0.6)` |
| **Classification** | Threshold-based: Fit (≥70%), Partial (≥40%), Reject (<40%) |
| **Vector Search** | pgvector for efficient similarity search |
| **Query Expansion** | Synonym mapping and fuzzy string matching |

---

## 4. Core Algorithms

### 4.1 Sentence-BERT Embeddings
```
Embedding(text) = BERT_encoder(text) → [384-dimensional vector]

Model: all-MiniLM-L6-v2 (Sentence-Transformers)
- Captures semantic meaning beyond keywords
- "React developer" ≈ "Frontend engineer" (semantically similar)
- "Java" (programming) ≠ "Java" (coffee) (context-aware)
```

### 4.2 Cosine Similarity
```
cosine(A, B) = (A · B) / (||A|| × ||B||)

Used for: Comparing TF-IDF vectors of job descriptions and resumes
```

### 4.3 Jaccard Similarity (Skill Matching)
```
jaccard(A, B) = |A ∩ B| / |A ∪ B|

Used for: Comparing skill sets between job requirements and candidate skills
```

### 4.4 Weighted Hybrid Score
```
Final Score = (α × Content_Similarity) + (β × Skill_Similarity)

Where: α = 0.4, β = 0.6 (skills weighted higher for technical roles)
```

### 4.5 Vector Search (pgvector)
```sql
-- PostgreSQL with pgvector extension
SELECT * FROM resumes 
ORDER BY embedding <=> query_embedding  -- Cosine distance
LIMIT 10;
```

---

## 5. Key Features

### ✅ Implemented Features
- [x] Sentence-BERT document embeddings (384-dim vectors)
- [x] Dense retrieval with semantic understanding
- [x] Cosine similarity for content matching
- [x] Jaccard similarity for skill matching
- [x] Weighted hybrid ranking system
- [x] Skill extraction with 400+ technical patterns
- [x] Fuzzy matching for typo tolerance
- [x] Synonym resolution (e.g., "JS" → "JavaScript")
- [x] Candidate classification (Fit/Partial/Reject)
- [x] Skill gap analysis with recommendations
- [x] pgvector for vector similarity search
- [x] LLM-powered match explanations
- [x] React frontend with real-time results
- [x] REST API with FastAPI

### 🔮 Future Enhancements
- [ ] Add user feedback loop for ranking improvement
- [ ] Implement dialogue-based query refinement
- [ ] Add geolocation-based job filtering
- [ ] Build recommendation engine for career paths
- [ ] Multi-language resume support

---

## 6. Dataset & Skills

The system includes a comprehensive skills database with:
- **Programming Languages**: Python, Java, JavaScript, C++, Go, Rust, etc.
- **Frameworks**: React, Angular, Django, Flask, Spring, etc.
- **Databases**: PostgreSQL, MongoDB, Redis, Elasticsearch, etc.
- **Cloud & DevOps**: AWS, Azure, GCP, Docker, Kubernetes, etc.
- **Data & ML**: TensorFlow, PyTorch, Pandas, Scikit-learn, etc.
- **Soft Skills**: Communication, Leadership, Problem-solving, etc.

---

## 7. Evaluation Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| **Precision** | Relevant candidates in top-k results | > 80% |
| **Recall** | Proportion of relevant candidates retrieved | > 75% |
| **F1-Score** | Harmonic mean of precision and recall | > 0.77 |
| **Silhouette Score** | Cluster quality for job domains | > 0.5 |
| **User Satisfaction** | Manual evaluation of match quality | > 4/5 |

---

## 8. Technology Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, Vite, Framer Motion |
| **Backend** | Python 3.10+, FastAPI |
| **Database** | PostgreSQL + pgvector |
| **Embeddings** | Sentence-Transformers (all-MiniLM-L6-v2) |
| **IR Engine** | Dense retrieval with cosine similarity |
| **NLP** | NLTK, Pattern matching |
| **LLM** | LM Studio (DeepSeek-R1) |
| **Deployment** | Docker, Docker Compose |

---

## 9. Alignment with Course Topics

This project demonstrates understanding of:

1. **Document Representation** - Dense vector embeddings (Sentence-BERT)
2. **Similarity Measures** - Cosine and Jaccard similarity
3. **Ranked Retrieval** - Score-based document ranking
4. **Query Processing** - Skill extraction and synonym expansion
5. **Vector Search** - Efficient similarity search with pgvector
6. **Evaluation** - Precision, Recall, F1-Score

---

## 10. Conclusion

This Resume-Job Matching System applies fundamental Information Retrieval concepts to solve a real-world recruitment problem. By combining TF-IDF document representation, similarity-based ranking, skill gap analysis, and job clustering, the system provides an end-to-end solution for automated candidate screening.

The modular architecture allows for future enhancement with neural embeddings (BERT) and reinforcement learning for adaptive ranking.

---

**Author**: Raj Kumar  
**Course**: Information Retrieval (Rejected/Too Common)
**Date**: February 2026
