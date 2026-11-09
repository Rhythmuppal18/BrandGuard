# BrandGuard - Production Docker Container
# CodeTitans India 2026 — Round 2 Build
FROM python:3.13-slim

WORKDIR /app

# Install system dependencies for document processing
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy source code and compiled static assets
COPY backend/ ./backend/
COPY frontend/dist/ ./frontend/dist/
COPY sample_documents/ ./sample_documents/
COPY run.py ./run.py
COPY README.md ./README.md

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["python", "run.py"]

