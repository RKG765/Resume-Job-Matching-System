# Resume-Job Matching System - Backend Dockerfile (Cloud-Ready)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the BERT model at build time (avoids download at runtime)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy source code
COPY . .

# Set Python path
ENV PYTHONPATH=/app/src

# Cloud platforms inject PORT env var (default 8000)
ENV PORT=8000

# Expose port
EXPOSE ${PORT}

# Run with uvicorn - uses $PORT from environment
CMD uvicorn src.main:app --host 0.0.0.0 --port $PORT
