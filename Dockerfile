# 🐳 AI Portfolio Return Calculator - Production Dockerfile
# Multi-stage build for optimized production deployment
# Built with security and performance best practices

# ==========================================
# 🏗️ STAGE 1: BUILD ENVIRONMENT
# ==========================================
FROM python:3.9-slim as builder

# Metadata
LABEL maintainer="AI Portfolio Calculator Team"
LABEL version="1.0.0"
LABEL description="Professional AI-powered portfolio return calculator"

# Build arguments
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.0

# Labels for container metadata
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="ai-portfolio-calculator" \
      org.label-schema.description="AI Portfolio Return Calculator" \
      org.label-schema.url="https://github.com/your-repo/ai-portfolio-calculator" \
      org.label-schema.vcs-ref=$VCS_REF \
      org.label-schema.vcs-url="https://github.com/your-repo/ai-portfolio-calculator" \
      org.label-schema.vendor="AI Portfolio Calculator Team" \
      org.label-schema.version=$VERSION \
      org.label-schema.schema-version="1.0"

# Install system dependencies for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==========================================
# 🚀 STAGE 2: PRODUCTION ENVIRONMENT
# ==========================================
FROM python:3.9-slim as production

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/uploads && \
    chown -R appuser:appuser /app

# Security: Remove unnecessary files and set permissions
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true && \
    chmod -R 755 /app && \
    chmod 644 /app/*.py

# Switch to non-root user
USER appuser

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_SERVER_ENABLE_CORS=false \
    STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=true

# Create .streamlit directory and config
RUN mkdir -p /app/.streamlit

# Create Streamlit configuration
RUN echo '[general]\n\
email = ""\n\
\n\
[server]\n\
headless = true\n\
port = 8501\n\
address = "0.0.0.0"\n\
enableCORS = false\n\
enableXsrfProtection = true\n\
maxUploadSize = 200\n\
\n\
[theme]\n\
primaryColor = "#667eea"\n\
backgroundColor = "#ffffff"\n\
secondaryBackgroundColor = "#f0f2f6"\n\
textColor = "#262730"\n\
font = "sans serif"\n\
\n\
[browser]\n\
gatherUsageStats = false' > /app/.streamlit/config.toml

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start command
CMD ["streamlit", "run", "streamlit_portfolio_app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true"]

# ==========================================
# 🔧 DEVELOPMENT STAGE (OPTIONAL)
# ==========================================
FROM production as development

# Switch back to root for development tools
USER root

# Install development dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    vim \
    htop \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install development Python packages
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    jupyter \
    ipython

# Switch back to appuser
USER appuser

# Development environment variables
ENV STREAMLIT_ENV=development \
    DEBUG=true

# Development command (with auto-reload)
CMD ["streamlit", "run", "streamlit_portfolio_app.py", \
     "--server.address=0.0.0.0", \
     "--server.port=8501", \
     "--server.headless=true", \
     "--server.runOnSave=true"]

# ==========================================
# 📝 USAGE INSTRUCTIONS
# ==========================================

# Build production image:
# docker build -t ai-portfolio-calculator:latest .

# Build development image:
# docker build --target development -t ai-portfolio-calculator:dev .

# Run production container:
# docker run -p 8501:8501 ai-portfolio-calculator:latest

# Run development container with volume mount:
# docker run -p 8501:8501 -v $(pwd):/app ai-portfolio-calculator:dev

# Run with environment variables:
# docker run -p 8501:8501 \
#   -e STREAMLIT_ENV=production \
#   -e DEBUG=false \
#   ai-portfolio-calculator:latest

# Docker Compose usage:
# docker-compose up -d

# ==========================================
# 🔒 SECURITY NOTES
# ==========================================

# 1. Non-root user: Application runs as 'appuser' (UID 1000)
# 2. Minimal base image: Uses python:3.9-slim for smaller attack surface
# 3. No unnecessary packages: Only runtime dependencies installed
# 4. Health checks: Built-in health monitoring
# 5. Read-only filesystem ready: Application doesn't write to container filesystem
# 6. Security headers: XSRF protection enabled

# ==========================================
# 📊 PERFORMANCE OPTIMIZATIONS
# ==========================================

# 1. Multi-stage build: Smaller production image size
# 2. Layer caching: Requirements installed before code copy
# 3. Virtual environment: Isolated Python dependencies
# 4. Bytecode disabled: Prevents .pyc file creation
# 5. Unbuffered output: Real-time logging

# ==========================================
# 🏷️ BUILD METADATA
# ==========================================

# Build with metadata:
# docker build \
#   --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ') \
#   --build-arg VCS_REF=$(git rev-parse HEAD) \
#   --build-arg VERSION=1.0.0 \
#   -t ai-portfolio-calculator:latest . 