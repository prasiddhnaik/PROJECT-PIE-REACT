FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY backup_cleanup/backend_python/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/web/package*.json ./apps/web/
WORKDIR /app/apps/web
RUN npm install

WORKDIR /app
COPY . .

WORKDIR /app/apps/web
RUN npm run build

WORKDIR /app
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Financial Analytics Platform..."\n\
cd backup_cleanup/backend_python\n\
python3 main.py &\n\
cd /app/apps/web\n\
npm start' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8001 3000

CMD ["/app/start.sh"] 