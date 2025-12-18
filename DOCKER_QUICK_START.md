`# 🐳 Docker Quick Reference - Smart Credit Risk Platform

## One-Liner: Build & Run in Docker

```bash
# Build
docker build -f Dockerfile.all-in-one -t credit-risk-platform:latest .

# Run
docker run -d --name credit-risk -p 3000:3000 -p 8000:8000 credit-risk-platform:latest
```

## Access Points
| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | React Dashboard |
| Backend API | http://localhost:8000 | FastAPI Server |
| API Docs | http://localhost:8000/docs | Interactive Swagger UI |
| Health Check | http://localhost:8000/health | API Status |

## Docker Desktop Steps

1. **Open Docker Desktop**
2. **Open Terminal/PowerShell** (inside Docker Desktop)
3. **Navigate to project**:
   ```bash
   cd C:\Users\awais\Desktop\mlll\smart-credit-risk-platform
   ```
4. **Build image**:
   ```bash
   docker build -f Dockerfile.all-in-one -t credit-risk-platform:latest .
   ```
5. **Run container**:
   ```bash
   docker run -d --name credit-risk -p 3000:3000 -p 8000:8000 credit-risk-platform:latest
   ```
6. **Check status**:
   ```bash
   docker ps
   ```
7. **View logs**:
   ```bash
   docker logs -f credit-risk
   ```

## Common Commands

| Command | Purpose |
|---------|---------|
| `docker ps` | Show running containers |
| `docker ps -a` | Show all containers |
| `docker logs credit-risk` | View logs |
| `docker logs -f credit-risk` | Follow logs (real-time) |
| `docker exec -it credit-risk bash` | Access container shell |
| `docker stop credit-risk` | Stop container |
| `docker start credit-risk` | Start container |
| `docker rm credit-risk` | Remove container |
| `docker rmi credit-risk-platform:latest` | Remove image |
| `docker stats credit-risk` | Monitor resources |

## What the Dockerfile Does

✅ **Stage 1**: Builds Python backend with ML libraries  
✅ **Stage 2**: Builds React frontend (optimized)  
✅ **Stage 3**: Combines both + Nginx + Supervisor  
✅ **Result**: Single container with frontend + backend  
✅ **Ports**: 3000 (frontend) + 8000 (backend)  

## File Size & Performance

| Metric | Value |
|--------|-------|
| Image Size | ~800MB-1GB |
| Build Time | 5-10 min (first) / 2-3 min (rebuild) |
| Memory Usage | ~500MB-1GB |
| CPU Usage | ~1-2% at idle |

## Clean Rebuild

```bash
# Stop and remove everything
docker stop credit-risk 2>/dev/null || true
docker rm credit-risk 2>/dev/null || true
docker rmi credit-risk-platform:latest 2>/dev/null || true

# Rebuild
docker build -f Dockerfile.all-in-one -t credit-risk-platform:latest .

# Run
docker run -d --name credit-risk -p 3000:3000 -p 8000:8000 credit-risk-platform:latest
```

## Troubleshooting

**Container won't start?**
```bash
docker logs credit-risk
```

**Port already in use?**
```bash
docker run -d --name credit-risk -p 3001:3000 -p 8001:8000 credit-risk-platform:latest
# Then access at http://localhost:3001
```

**Check if backend is running:**
```bash
docker exec credit-risk curl http://127.0.0.1:8000/health
```

---

📖 Full guide: See `DOCKER_GUIDE.md`
