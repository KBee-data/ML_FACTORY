FROM python:3.11-slim

WORKDIR /app

# Prevent Python buffering issues in Docker logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (needed for numpy / sklearn)
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file
COPY pyproject.toml .

# Install dependencies using pip
RUN pip install --no-cache-dir .

# Copy project code
COPY . .

# Start FastAPI
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]