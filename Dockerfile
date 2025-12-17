# ============================================
# SMART CREDIT RISK PLATFORM - COMBINED DOCKERFILE
# Builds and runs both Frontend (React) and Backend (FastAPI) in one container
# 
# Usage:
#   docker build -f Dockerfile -t credit-risk-platform .
#   docker run -p 3000:3000 -p 8000:8000 credit-risk-platform
#
# Access:
#   Frontend: http://localhost:3000
#   Backend API: http://localhost:8000
#   API Docs: http://localhost:8000/docs
# ============================================

# ============================================
# STAGE 1: Build Python Backend Dependencies
# ============================================
FROM python:3.11-slim as backend-builder

WORKDIR /backend-build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements-runtime.txt .
RUN pip install --user --no-cache-dir -r requirements-runtime.txt


# ============================================
# STAGE 2: Build React Frontend
# ============================================
FROM node:18-alpine as frontend-builder

WORKDIR /frontend-build

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies and build tools
RUN npm ci --only=production && \
    npm install react-scripts

# Copy application code
COPY frontend/ ./

# Build React app
RUN npm run build

# ============================================
# STAGE 3: Final Image - Combined Backend & Frontend
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies (nginx, supervisor, curl)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from backend builder
COPY --from=backend-builder /root/.local /root/.local

# Copy backend application code
COPY app ./app
COPY ml ./ml
COPY models ./models
COPY data ./data

# Copy frontend build from frontend builder to nginx directory
COPY --from=frontend-builder /frontend-build/build /usr/share/nginx/html

# Configure nginx for frontend with proxy to backend API
RUN mkdir -p /etc/nginx/conf.d && echo 'server { \
    listen 3000; \
    client_max_body_size 50M; \
    root /usr/share/nginx/html; \
    index index.html index.htm; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://127.0.0.1:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    location /health { \
        proxy_pass http://127.0.0.1:8000/health; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Configure supervisor to run both backend and nginx
RUN mkdir -p /etc/supervisor/conf.d && echo '[supervisord] \
nodaemon=true \
logfile=/var/log/supervisor/supervisord.log \
\
[program:backend] \
command=/root/.local/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 \
directory=/app \
stdout_logfile=/var/log/supervisor/backend.log \
stderr_logfile=/var/log/supervisor/backend.err.log \
autostart=true \
autorestart=true \
\
[program:nginx] \
command=/usr/sbin/nginx -g "daemon off;" \
stdout_logfile=/var/log/supervisor/nginx.log \
stderr_logfile=/var/log/supervisor/nginx.err.log \
autostart=true \
autorestart=true' > /etc/supervisor/conf.d/services.conf

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose both ports
EXPOSE 3000 8000

# Start supervisor which manages both backend and frontend
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/services.conf"]
# Backend: Smart Credit Risk Platform API
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements-runtime.txt .
RUN pip install --user --no-cache-dir -r requirements-runtime.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application code
COPY app ./app
COPY ml ./ml
COPY models ./models
COPY data ./data

# Set environment variables
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

EXPOSE 8000

