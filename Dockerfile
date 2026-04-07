# Use a specific slim Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
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

# Create a non-root user and set permissions
RUN useradd -m econavuser && \
    chown -R econavuser:econavuser /app
USER econavuser

# Expose the standard Hugging Face Space port
EXPOSE 7860

# Healthcheck to verify the server is running
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:7860/tasks || exit 1

# Start the application using uvicorn correctly
CMD ["uvicorn", "apps.backend.main:app", "--host", "0.0.0.0", "--port", "7860"]
