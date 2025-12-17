# Docker Setup Guide for Smart Credit Risk Platform

## Quick Start

### Build the combined Docker image:
```bash
cd smart-credit-risk-platform
docker build -f Dockerfile.all-in-one -t credit-risk-platform:latest .
```

### Run the container:
```bash
docker run -d \
  --name credit-risk \
  -p 3000:3000 \
  -p 8000:8000 \
  credit-risk-platform:latest
```

### Access the application:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## What's in the Combined Dockerfile

The `Dockerfile.all-in-one` uses **3-stage build** process:

### Stage 1: Backend Builder
- Builds Python dependencies from `requirements-runtime.txt`
- Creates optimized Python environment
- Installs ML libraries (scikit-learn, pandas, numpy, joblib, etc.)

### Stage 2: Frontend Builder
- Builds React app from `frontend/` directory
- Compiles to optimized production bundle
- Outputs to `/frontend-build/build`

### Stage 3: Final Combined Image
- Combines backend (FastAPI) and frontend (React via Nginx)
- Uses **Supervisor** to manage both processes
- Nginx on port 3000 (frontend + API proxy)
- FastAPI on port 8000 (backend API)
- Both services auto-restart if they crash

---

## Supervisor Configuration

The container runs **2 services** managed by Supervisor:

1. **Backend (Uvicorn)**
   - Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Auto-restarts on failure
   - Logs: `/var/log/supervisor/backend.log`

2. **Frontend (Nginx)**
   - Serves React build on port 3000
   - Proxies `/api/` calls to backend on port 8000
   - Auto-restarts on failure
   - Logs: `/var/log/supervisor/nginx.log`

---

## Docker Desktop Usage

### Option 1: Using Docker Desktop GUI
1. Open **Docker Desktop**
2. Go to **Images** tab
3. Click **Build** button
4. Select `Dockerfile.all-in-one`
5. Tag as `credit-risk-platform:latest`
6. Go to **Containers** and click **Run**
7. Set:
   - Port mapping: `3000:3000` and `8000:8000`
   - Container name: `credit-risk`
8. Click **Run**

### Option 2: Using Docker Desktop Terminal
```bash
# Open PowerShell or Terminal in Docker Desktop

# Navigate to project
cd C:\Users\awais\Desktop\mlll\smart-credit-risk-platform

# Build
docker build -f Dockerfile.all-in-one -t credit-risk-platform:latest .

# Run
docker run -d --name credit-risk -p 3000:3000 -p 8000:8000 credit-risk-platform:latest

# View logs
docker logs -f credit-risk

# Stop container
docker stop credit-risk

# Remove container
docker rm credit-risk
```

---

## Useful Docker Commands

### View running containers:
```bash
docker ps
```

### View all containers:
```bash
docker ps -a
```

### View container logs:
```bash
docker logs credit-risk
docker logs -f credit-risk  # Follow logs in real-time
```

### Execute command in container:
```bash
docker exec -it credit-risk bash
docker exec -it credit-risk /bin/bash
```

### Remove container:
```bash
docker stop credit-risk
docker rm credit-risk
```

### Remove image:
```bash
docker rmi credit-risk-platform:latest
```

### Rebuild and run (clean start):
```bash
docker stop credit-risk 2>/dev/null || true
docker rm credit-risk 2>/dev/null || true
docker rmi credit-risk-platform:latest 2>/dev/null || true
docker build -f Dockerfile.all-in-one -t credit-risk-platform:latest .
docker run -d --name credit-risk -p 3000:3000 -p 8000:8000 credit-risk-platform:latest
```

---

## Troubleshooting

### Container exits immediately:
```bash
docker logs credit-risk
```
Check logs for errors. Common issues:
- Port already in use: Change port mapping `-p 3001:3000`
- Missing dependencies: Rebuild image
- Python errors: Check ML models and requirements

### Can't access frontend at localhost:3000:
- Verify container is running: `docker ps`
- Check firewall settings
- Try accessing via container IP: `docker inspect credit-risk` (look for IPAddress)

### Backend API not responding:
- Check if backend service is running: `docker exec credit-risk curl http://127.0.0.1:8000/health`
- View backend logs: `docker logs credit-risk | grep backend`

### Models not loading:
- Ensure `/models` directory has all .pkl and .joblib files
- Rebuild image if models were recently retrained

### High memory usage:
- Supervisor + Nginx + Python uses ~500MB-1GB
- Use `docker stats` to monitor: `docker stats credit-risk`

---

## File Structure in Container

```
/app/
├── app/
│   ├── main.py (FastAPI app)
│   ├── predict.py (ML predictions)
│   └── schemas.py (Request/Response models)
├── ml/
│   ├── train.py
│   ├── prepare_data.py
│   ├── features.py
│   └── evaluate.py
├── models/
│   ├── classification_model.pkl
│   ├── regression_model.pkl
│   ├── clustering_model.pkl
│   ├── pca_model.pkl
│   ├── preprocessor.joblib
│   └── preprocessor_config.joblib
├── data/
│   ├── bank_loan.csv (training data)
│   └── processed/
└── /usr/share/nginx/html/
    └── (React build output)
```

---

## Performance Notes

- **Build time**: ~5-10 minutes (first time)
- **Rebuild time**: ~2-3 minutes (cached layers)
- **Container size**: ~800MB-1GB
- **Memory usage**: ~500MB-1GB
- **CPU usage**: Low (~1-2%) at idle

---

## Next Steps

After container is running, you can:

1. **Test the API**:
   ```bash
   curl http://localhost:8000/health
   curl -X POST http://localhost:8000/docs  # Interactive API docs
   ```

2. **Deploy to production**:
   - Push to Docker Hub
   - Deploy to AWS ECS, Kubernetes, or DigitalOcean
   - Use docker-compose for multi-container orchestration

3. **Monitor logs**:
   ```bash
   docker logs -f credit-risk
   ```

---

## Alternative: Using Docker Compose

Instead of running individual containers, use `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.all-in-one
    container_name: credit-risk
    ports:
      - "3000:3000"
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
    restart: unless-stopped
```

Then run:
```bash
docker-compose up -d
docker-compose logs -f
docker-compose down
```

---

For more information, see the main README.md or DEPLOYMENT.md
