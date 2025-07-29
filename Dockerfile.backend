FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python backend requirements and install
COPY backup_cleanup/backend_python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backup_cleanup/backend_python/ ./backend/

# Set environment variables
ENV API_HOST=0.0.0.0
ENV API_PORT=8001
ENV DEBUG=False
ENV PYTHONPATH=/app/backend

EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the backend with proper error handling
CMD ["python", "-u", "backend/main.py"] 