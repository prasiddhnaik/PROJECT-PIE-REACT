# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backup_cleanup/backend_python/requirements.txt ./requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Financial Analytics Platform..."\n\
echo "📊 Backend: Starting FastAPI server..."\n\
cd backup_cleanup/backend_python\n\
python3 main.py &\n\
BACKEND_PID=$!\n\
echo "✅ Backend started with PID: $BACKEND_PID"\n\
\n\
echo "🌐 Frontend: Building Next.js app..."\n\
cd /app/apps/web\n\
npm install\n\
npm run build\n\
npm start &\n\
FRONTEND_PID=$!\n\
echo "✅ Frontend started with PID: $FRONTEND_PID"\n\
\n\
echo "🎉 Platform is running!"\n\
echo "📊 Backend API: http://localhost:8001"\n\
echo "🌐 Frontend: http://localhost:3000"\n\
echo "🏥 Health Check: http://localhost:8001/health"\n\
\n\
# Wait for both processes\n\
wait $BACKEND_PID $FRONTEND_PID' > /app/start.sh

RUN chmod +x /app/start.sh

# Expose ports
EXPOSE 8001 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1

# Start the platform
CMD ["/app/start.sh"] 