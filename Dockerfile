FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip install --no-cache-dir -r backup_cleanup/backend_python/requirements.txt

WORKDIR /app/apps/web
RUN npm install
RUN npm run build

WORKDIR /app
RUN echo '#!/bin/bash\n\
cd backup_cleanup/backend_python\n\
python3 main.py &\n\
cd /app/apps/web\n\
npm start' > /app/start.sh

RUN chmod +x /app/start.sh

EXPOSE 8001 3000

CMD ["/app/start.sh"] 