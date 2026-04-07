<<<<<<< HEAD
<<<<<<< HEAD
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
=======
FROM python:3.11-slim
=======
# Use a specific slim Python image that matches openenv.yaml
FROM python:3.10-slim
>>>>>>> d2e1b4b9512e639ac575782b92da2848e710b592

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Set working directory
WORKDIR /app

# Install system dependencies
# Install system dependencies with better error handling and common tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install --no-cache-dir uv

# Copy ONLY requirements first to leverage Docker cache
COPY requirements/ ./requirements/
COPY pyproject.toml uv.lock ./

# Install project dependencies with uv
RUN uv pip install --system --no-cache -r requirements/backend.txt -r requirements/ml.txt

# Copy the rest of the application
COPY . .

# Set up a new user named "user" with UID 1000 for HF Spaces compatibility
RUN useradd -m -u 1000 user && \
    chown -R user:user /app
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Expose the standard Hugging Face Space port
EXPOSE 7860

<<<<<<< HEAD
# Run the FastAPI app on the port HF expects
>>>>>>> 1c2f25b401a67215ea459ece945cb72cc7dbd373
=======
# No HEALTHCHECK needed for standard HF Spaces and validator deployments,
# simplifies build logic and reduces potential for false failures.

# Start the application using uvicorn correctly
>>>>>>> d2e1b4b9512e639ac575782b92da2848e710b592
CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
