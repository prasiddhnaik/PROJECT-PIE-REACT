FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy Python backend requirements and install
COPY backend/backend_python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend/backend_python/ ./backend/

# Set environment variables
ENV API_HOST=0.0.0.0
ENV DEBUG=False
ENV PYTHONPATH=/app/backend

# Let Render set the PORT environment variable
EXPOSE 10000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:10000/health || exit 1

# Copy startup script
COPY start.sh ./start.sh

# Start the backend with proper error handling
# Try simplified version first, fallback to full version
CMD ["python", "-u", "backend/main_simple.py"] 