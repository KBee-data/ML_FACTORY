# src/front/Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Minimal environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (only what Streamlit needs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages needed for frontend only
RUN pip install --no-cache-dir streamlit requests python-dotenv

# Copy only the frontend code
COPY src/front ./src/front

# Expose Streamlit port
EXPOSE 8501

# Command to run the Streamlit app
CMD ["streamlit", "run", "src/front/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]