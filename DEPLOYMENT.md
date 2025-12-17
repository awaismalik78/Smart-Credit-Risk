# 🚀 Deployment Guide - Smart Credit Risk Platform

## Quick Deployment Options

### Option 1: Local Development (5 minutes)

```bash
# Clone & Setup
git clone <repo>
cd smart-credit-risk-platform
python -m venv .venv
source .venv/Scripts/activate  # Windows
source .venv/bin/activate      # macOS/Linux

# Install
pip install fastapi uvicorn pandas numpy scikit-learn joblib requests

# Run API (Terminal 1)
python -m uvicorn app.main:app --reload --port 8000

# Run Frontend (Terminal 2)
cd frontend
npm install
npm start
```

**Access**:
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

---

### Option 2: Docker Compose (Production)

```bash
# Start all services
docker-compose up -d

# Verify services
docker-compose ps

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down
```

**Access**:
- API: http://localhost:8000
- Dashboard: http://localhost:3000
- Prefect: http://localhost:4200

---

### Option 3: Individual Docker Containers

```bash
# Build backend
docker build -t credit-risk-api:latest .

# Build frontend
docker build -f Dockerfile.frontend -t credit-risk-frontend:latest .

# Run backend
docker run -d -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  --name credit-api \
  credit-risk-api:latest

# Run frontend
docker run -d -p 3000:80 \
  --name credit-ui \
  credit-risk-frontend:latest

# Test
curl http://localhost:8000/health
```

---

## Pre-Deployment Checklist

- [ ] Dataset at `data/bank_loan.csv`
- [ ] Models in `models/` directory
  - [ ] `classification_model.pkl`
  - [ ] `regression_model.pkl`
  - [ ] `clustering_model.pkl`
  - [ ] `preprocessor.joblib`
- [ ] All dependencies installed
- [ ] Tests passing: `pytest tests/ -v`
- [ ] Health check: `curl http://localhost:8000/health`
- [ ] No sensitive data in code
- [ ] Environment variables configured
- [ ] Logs directory writable

---

## Environment Variables

Create `.env` file:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
LOG_LEVEL=INFO

# Database (if using later)
DATABASE_URL=postgresql://user:password@localhost/dbname

# Frontend
REACT_APP_API_URL=http://localhost:8000

# Prefect (if using)
PREFECT_API_URL=http://localhost:4200/api
```

Load in Python:
```python
from dotenv import load_dotenv
load_dotenv()
```

---

## Health Checks

### API Health
```bash
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

### Test Classification
```bash
curl -X POST http://localhost:8000/predict/classification \
  -H "Content-Type: application/json" \
  -d '{
    "loan_amount": 5000,
    "interest_rate": 5.5,
    "income": 50000,
    "employment_length": 5,
    "purpose": "debt_consolidation",
    "term": 36,
    "credit_score": 700,
    "monthly_debt": 1000,
    "years_of_credit_history": 10,
    "loan_status": "approved"
  }'
```

### Test Frontend
```bash
curl http://localhost:3000/
# Should return HTML
```

---

## Monitoring & Logs

### Docker Logs
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs api
docker-compose logs frontend

# Follow logs
docker-compose logs -f api
```

### Application Logs
```bash
# API logs (console output)
# Frontend browser console: F12

# Prefect logs
prefect server start  # UI at http://localhost:4200
```

---

## Model Training & Update

### One-time Training
```bash
python -m ml.prepare_data
python -m ml.train
```

### Using Prefect
```bash
python prefect/flow.py
```

### Using GitHub Actions
- Automatic daily training (2 AM UTC)
- Manual trigger via Actions tab

---

## Performance Tuning

### API Performance
```bash
# Increase workers for high concurrency
uvicorn app.main:app --workers 4 --port 8000
```

### Docker Resource Limits
```yaml
# docker-compose.yml
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

---

## Troubleshooting

### Models Not Found
```bash
# Train models
python -m ml.train

# Verify
ls models/
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process or use different port
python -m uvicorn app.main:app --port 8001
```

### CORS Errors
```python
# Already handled in app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Docker Build Fails
```bash
# Clean up
docker system prune -a

# Rebuild
docker-compose build --no-cache
```

---

## Production Best Practices

### 1. Security
```bash
# Change CORS to specific origins
allow_origins=["https://yourdomain.com"]

# Use environment variables for secrets
from os import getenv
SECRET_KEY = getenv("SECRET_KEY")

# Enable HTTPS
# Use reverse proxy (nginx)
```

### 2. Scaling
```yaml
# docker-compose.yml - Scale services
services:
  api:
    deploy:
      replicas: 3  # Run 3 instances
```

### 3. Monitoring
```bash
# Add prometheus/grafana
# Monitor API response times
# Track model performance
```

### 4. Backup
```bash
# Backup models
tar -czf models_backup_$(date +%Y%m%d).tar.gz models/

# Backup data
tar -czf data_backup_$(date +%Y%m%d).tar.gz data/
```

---

## Scaling to Production

### Load Balancing
```nginx
# nginx.conf
upstream api {
    server api1:8000;
    server api2:8000;
    server api3:8000;
}

server {
    listen 80;
    location /api {
        proxy_pass http://api;
    }
}
```

### Database Integration
```python
# app/database.py
from sqlalchemy import create_engine
engine = create_engine(os.getenv("DATABASE_URL"))

# Store predictions for analytics
```

### Model Registry
```bash
# Version models
mv models/classification_model.pkl models/classification_model_v1.pkl

# Track versions
git tag -a v1.0 -m "Model v1.0"
```

---

## Deployment to Cloud

### AWS
```bash
# Push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag credit-risk-api:latest <account>.dkr.ecr.us-east-1.amazonaws.com/credit-risk-api:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/credit-risk-api:latest

# Deploy to ECS or EKS
```

### Google Cloud
```bash
# Configure gcloud
gcloud config set project <PROJECT_ID>

# Push to GCR
gcloud builds submit --tag gcr.io/<PROJECT_ID>/credit-risk-api

# Deploy to Cloud Run
gcloud run deploy credit-risk-api --image gcr.io/<PROJECT_ID>/credit-risk-api --platform managed
```

### Kubernetes
```yaml
# k8s/deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: credit-risk-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: credit-risk-api:latest
        ports:
        - containerPort: 8000
```

---

## Monitoring & Observability

### Prometheus Metrics
```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

@app.post("/predict/classification")
def predict(input: LoanInput):
    logger.info(f"Classification prediction: {input.loan_amount}")
    result = predict_classification(input.dict())
    logger.info(f"Result: {result}")
    return result
```

### Error Tracking
```python
import sentry_sdk
sentry_sdk.init("https://examplePublicKey@o0.ingest.sentry.io/0")
```

---

## Maintenance

### Regular Tasks
- [ ] Daily: Check health endpoints
- [ ] Weekly: Review logs and metrics
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Retrain models
- [ ] Annually: Security audit

### Backup Schedule
```bash
# Daily backup
0 2 * * * tar -czf /backups/models_$(date +\%Y\%m\%d).tar.gz /app/models/

# Weekly data backup
0 3 * * 0 tar -czf /backups/data_$(date +\%Y\%m\%d).tar.gz /app/data/
```

---

## Support

**Documentation**: See README.md  
**Issues**: GitHub Issues tab  
**Contact**: Contact support team

---

**Last Updated**: December 17, 2025  
**Version**: 1.0.0
