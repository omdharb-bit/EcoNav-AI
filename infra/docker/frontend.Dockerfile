FROM python:3.11-slim

WORKDIR /app

COPY requirements /app/requirements
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements/frontend.txt

COPY . /app

EXPOSE 8501
CMD ["streamlit", "run", "apps/frontend/app.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
