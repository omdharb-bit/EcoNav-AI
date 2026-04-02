FROM python:3.10-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy project
COPY . .

# Install Python deps
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
    fastapi>=0.111 \
    uvicorn>=0.30 \
    requests>=2.32 \
    pydantic>=2.7 \
    numpy>=1.26 \
    openai>=1.0 \
    pyyaml>=6.0

# Expose port (HF Spaces uses 7860)
EXPOSE 7860

# Set pythonpath so imports work
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

# Start server
CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
