# syntax=docker/dockerfile:1
# -------------------------------------------------------------
# 🚀 Financial Analytics Hub – Backend Docker image (slim)
# -------------------------------------------------------------
# 1. builder stage installs dependencies into a virtual env layer
# 2. runtime stage copies only the virtual env and app source → tiny image
#
# Build:   docker build -t fa-backend:latest ./services/backend
# Run:     docker run -p 8001:8000 --env-file .env fa-backend:latest
# -------------------------------------------------------------

FROM python:3.11-slim-bookworm AS builder

# Install system deps needed for some wheels (pandas, numpy, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python deps to /install – will be copied later
COPY requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ------------------------------------------------------------------
# Final stage: copy minimal runtime bits
# ------------------------------------------------------------------
FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/install/bin:$PATH"

# Copy installed packages from builder
COPY --from=builder /install /install

WORKDIR /app
COPY . .

# Expose port that uvicorn will bind to (aligned with microservices architecture)
EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"] 
 
 
 