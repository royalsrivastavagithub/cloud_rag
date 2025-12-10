# ---- Base image ----
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (Chroma + some Python libs need them)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Python dependencies ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy application code ----
COPY . .

# Create directories used at runtime (ignored in git)
RUN mkdir -p aws_logs vector_db

# Expose FastAPI port
EXPOSE 8000

# Environment (override using docker run -e)
ENV PYTHONUNBUFFERED=1

# ---- Start the FastAPI server ----
CMD ["python", "main.py"]
