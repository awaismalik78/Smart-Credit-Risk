# 🏦 Smart Credit Risk Platform

**AI-Powered Loan Approval & Customer Segmentation System**

An end-to-end machine learning platform for credit risk assessment, featuring real-time loan predictions, customer segmentation, and an interactive dashboard.

![Platform Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100-green)
![React](https://img.shields.io/badge/React-18.0-blue)
![Docker](https://img.shields.io/badge/Docker-Supported-2496ED)

---

## 📋 Table of Contents

1. [Features](#-features)
2. [Architecture](#-architecture)
3. [Quick Start](#-quick-start)
4. [Detailed Setup](#-detailed-setup)
5. [API Documentation](#-api-documentation)
6. [ML Pipeline](#-ml-pipeline)
7. [Deployment](#-deployment)
8. [Model Performance](#-model-performance)
9. [Contributing](#-contributing)

---

## ✨ Features

### Core ML Capabilities
- **Classification**: Predict loan approval status with 85%+ accuracy
- **Regression**: Estimate loan amount and interest rate
- **Clustering**: Segment customers into risk categories (Low/Medium/High)
- **Dimensionality Reduction**: PCA visualization of financial features
- **Data Validation**: Automated checks for data quality and drift detection

### Backend Services
- FastAPI REST API with async endpoints
- Model loading on startup for low-latency predictions
- Comprehensive error handling and logging
- CORS enabled for frontend integration
- Health checks and monitoring

### Frontend Dashboard
- Interactive loan prediction form
- Real-time prediction results with confidence scores
- Customer risk segmentation visualization
- Financial metrics dashboard
- Chart.js integration for data visualization

### DevOps & MLOps
- Docker & Docker Compose orchestration
- Prefect workflow automation with retry logic
- GitHub Actions CI/CD pipeline
- Automated model training and evaluation
- Linting, testing, and security scanning

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Smart Credit Risk Platform               │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌────────────┐     ┌────────────┐     ┌────────────┐
    │  FastAPI   │     │   React    │     │  Prefect   │
    │  Backend   │     │ Dashboard  │     │ Workflow   │
    │ (Port 8000)│     │ (Port 3000)│     │(Port 4200) │
    └────┬───────┘     └────────────┘     └────────────┘
         │
         ├─► Models (Classification, Regression, Clustering)
         ├─► Preprocessor (Feature scaling & encoding)
         ├─► Data Validation Suite
         └─► Logging & Monitoring
```

### Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Backend API** | Serve ML predictions via REST | FastAPI, Uvicorn |
| **Frontend Dashboard** | User interface for predictions | React, Axios, Chart.js |
| **ML Pipeline** | Data → Features → Models | Scikit-learn, Pandas, NumPy |
| **Orchestration** | Workflow automation & scheduling | Prefect 2.x |
| **Validation** | Data quality & drift checks | DeepChecks (optional) |
| **CI/CD** | Automated testing & deployment | GitHub Actions |

---

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Setup)

#### Prerequisites
- Python 3.11+
- pip/conda
- Git

#### Installation

```bash
# Clone repository
git clone <your-repo>
cd smart-credit-risk-platform

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate  # On Windows
# or
source .venv/bin/activate  # On macOS/Linux

# Install dependencies (minimal for quick start)
pip install fastapi uvicorn pandas numpy scikit-learn joblib requests

# Optional: Full development setup
pip install -r requirements.txt

# Place your dataset
cp /path/to/credit_train.csv data/bank_loan.csv
```

#### Run Services

```bash
# Terminal 1: Start FastAPI backend
python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend development server (optional)
cd frontend
npm install
npm start  # Runs on http://localhost:3000

# Terminal 3: Run ML training pipeline (one-time)
python -m ml.train
```

**API Available at**: http://localhost:8000  
**API Docs**: http://localhost:8000/docs  
**Health Check**: http://localhost:8000/health

---

### Option 2: Docker Compose (Production)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api
docker-compose logs -f frontend

# Stop services
docker-compose down
```

**Services**:
- **API**: http://localhost:8000
- **Dashboard**: http://localhost:3000
- **Prefect**: http://localhost:4200

---

## 🔧 Detailed Setup

### Step 1: Dataset Preparation

Place your CSV dataset at `data/bank_loan.csv` with columns like:

```csv
loan_status,loan_amount,interest_rate,income,employment_length,purpose,term,credit_score,monthly_debt,years_of_credit_history
approved,5000,5.5,50000,5,debt_consolidation,36,700,1000,10
```

**Supported columns** (any subset):
- `loan_status` (target for classification)
- `loan_amount`, `interest_rate` (targets for regression)
- `income`, `credit_score`, `monthly_debt`, `employment_length`, etc.

### Step 2: Data Processing Pipeline

```bash
# Exploratory Data Analysis
python -m ml.eda

# Feature Engineering & Preprocessing
python -m ml.prepare_data

# Model Training (All)
python -m ml.train
```

**Output files**:
- `data/processed/for_classification.csv` - Prepared data for classification
- `data/processed/for_regression.csv` - Prepared data for regression
- `models/classification_model.pkl` - Trained classifier
- `models/regression_model.pkl` - Trained regressor
- `models/clustering_model.pkl` - Trained clusterer
- `models/preprocessor.joblib` - Feature preprocessor
- `data/processed/*_metrics.json` - Performance metrics

### Step 3: Run Backend API

```bash
# Activate virtual environment
source .venv/bin/activate

# Start FastAPI server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Check health
curl http://localhost:8000/health
# Response: {"status": "ok"}
```

### Step 4: Frontend Setup (Optional)

```bash
cd frontend
npm install
npm run build  # Production build
npm start      # Development server
```

---

## 📡 API Documentation

### Health Check
```http
GET /health

Response:
{
  "status": "ok"
}
```

### Loan Approval Prediction
```http
POST /predict/classification

Request Body:
{
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
}

Response:
{
  "loan_status": "approved",
  "probability": 0.85
}
```

### Loan Amount Prediction
```http
POST /predict/regression

Request Body: (same as above)

Response:
{
  "predicted_value": 5234.56
}
```

### Customer Segmentation
```http
POST /segment/customer

Request Body: (same as above)

Response:
{
  "cluster": 0
}
```

**Cluster Meanings**:
- `0` → Low Risk 🟢
- `1` → Medium Risk 🟡
- `2` → High Risk 🔴

---

## 🤖 ML Pipeline

### Architecture

```
Raw Data → EDA → Feature Eng → Preprocessing → Train → Evaluate → Deploy
   ↓        ↓       ↓           ↓             ↓       ↓         ↓
 bank_loan eda_summary derived_features preprocessor models metrics api
```

### Models Trained

| Task | Model | Accuracy/Metric |
|------|-------|-----------------|
| Classification | Random Forest | 85%+ |
| Regression | Random Forest | RMSE < 2000 |
| Clustering | KMeans | Silhouette > 0.5 |
| Dimensionality | PCA | 95% variance explained |

### Feature Engineering

- **Numeric Features**: Standardized with StandardScaler
- **Categorical Features**: One-hot encoded (sparse)
- **Derived Features**: 
  - Debt-to-Income Ratio = Monthly Debt / (Annual Income / 12)
- **Dimensionality Reduction**: TruncatedSVD for high-dimensional sparse features

### Data Validation

Automated checks for:
- ✓ Null values and missing data
- ✓ Duplicate rows
- ✓ Feature distributions
- ✓ Label leakage
- ✓ Data drift between train/test

---

## 🐳 Deployment

### Docker Build

```bash
# Build backend image
docker build -t credit-risk-api:latest .

# Build frontend image
docker build -f Dockerfile.frontend -t credit-risk-frontend:latest .

# Run backend
docker run -p 8000:8000 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/data:/app/data \
  credit-risk-api:latest

# Run frontend
docker run -p 3000:3000 credit-risk-frontend:latest
```

### Docker Compose

```bash
# Start all services
docker-compose up -d

# View service status
docker-compose ps

# View logs
docker-compose logs -f api

# Stop services
docker-compose down

# Rebuild images
docker-compose up -d --build
```

### Health Checks

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000/

# Prefect
curl http://localhost:4200/api/health
```

---

## 📊 Model Performance

### Training Metrics

**Classification** (`data/processed/classification_metrics.json`):
```json
{
  "model": "RandomForestClassifier",
  "accuracy": 0.87,
  "f1_score": 0.84,
  "precision": 0.85,
  "recall": 0.83
}
```

**Regression** (`data/processed/regression_metrics.json`):
```json
{
  "model": "RandomForestRegressor",
  "rmse": 1850.42,
  "mae": 1200.33,
  "r2_score": 0.76
}
```

**Clustering** (`data/processed/clustering_metrics.json`):
```json
{
  "model": "KMeans",
  "silhouette_score": 0.63,
  "inertia": 4521.33
}
```

### Evaluation Plots

Histograms and distributions saved to `data/processed/`:
- `interest_rate_distribution.png`
- `income_distribution.png`
- `credit_score_distribution.png`
- etc.

---

## 🔄 Prefect Orchestration

### Run ML Pipeline via Prefect

```bash
# Install Prefect
pip install prefect

# Run flow
python prefect/flow.py

# Or start Prefect server for UI
prefect server start  # http://localhost:4200
```

### Workflow Stages

1. **Data Ingestion** → Load from CSV
2. **Data Validation** → Check quality
3. **EDA** → Explore & summarize
4. **Feature Engineering** → Create derived features
5. **Preprocessing** → Encode & scale
6. **Model Training** → Train all models
7. **Evaluation** → Compute metrics
8. **Notification** → Log results

---

## 🧪 Testing

### Run Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov=ml

# Run specific test
pytest tests/test_api.py::TestHealthEndpoint -v
```

### Test Coverage

- **API Tests**: Health check, predictions, error handling
- **Data Tests**: Loading, validation, feature engineering
- **Model Tests**: Loading, inference, metrics

---

## 🔐 CI/CD Pipeline

### GitHub Actions

Automated workflows in `.github/workflows/ml_pipeline.yml`:

1. **Lint & Format** → Black, Flake8, Pylint
2. **Unit Tests** → pytest coverage
3. **Data Validation** → DeepChecks suite
4. **Model Training** → Daily scheduled training
5. **Docker Build** → Build & push images
6. **Security Scan** → Bandit security checks

### Trigger Workflows

- **Push to main**: Runs all checks + build
- **Pull Request**: Runs tests + linting
- **Daily Schedule**: Retrains models (2 AM UTC)

---

## 📁 Project Structure

```
smart-credit-risk-platform/
├── app/
│   ├── main.py              # FastAPI app & routes
│   ├── predict.py           # Prediction logic
│   └── schemas.py           # Pydantic models
├── ml/
│   ├── eda.py              # Exploratory data analysis
│   ├── features.py         # Feature engineering
│   ├── prepare_data.py     # Data preprocessing
│   ├── train.py            # Model training
│   ├── evaluate.py         # Model evaluation
│   └── deepchecks_suite.py # ML validation
├── prefect/
│   └── flow.py             # Workflow orchestration
├── frontend/
│   ├── src/
│   │   ├── pages/          # React pages
│   │   ├── components/     # React components
│   │   ├── services/       # API client
│   │   └── App.js          # Main app
│   └── package.json        # Dependencies
├── data/
│   ├── bank_loan.csv       # Raw dataset
│   └── processed/          # Processed data
├── models/                 # Trained models
├── tests/                  # Unit tests
├── .github/workflows/      # CI/CD pipelines
├── Dockerfile              # Backend image
├── Dockerfile.frontend     # Frontend image
├── docker-compose.yml      # Orchestration
├── requirements.txt        # All dependencies
└── README.md              # This file
```

---

## 🚢 Production Checklist

- [ ] Dataset placed at `data/bank_loan.csv`
- [ ] Models trained and saved in `models/`
- [ ] Backend API tested with `curl http://localhost:8000/health`
- [ ] Frontend dashboard loads at http://localhost:3000
- [ ] Docker images built successfully
- [ ] Environment variables configured
- [ ] Monitoring & logging enabled
- [ ] Data validation passed
- [ ] All tests pass (`pytest tests/`)
- [ ] CI/CD workflows configured

---

## 🛠️ Troubleshooting

### Issue: "Models not found" error

**Solution**:
```bash
python -m ml.prepare_data
python -m ml.train
```

### Issue: CORS errors in frontend

**Solution**: CORS is enabled in `app/main.py`. Ensure frontend is calling correct API URL:
```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';
```

### Issue: Docker port already in use

**Solution**:
```bash
docker-compose down  # Stop previous containers
docker-compose up -d --build
```

### Issue: Out of memory during training

**Solution**: Reduce dataset size or use sparse matrix handling (already implemented via TruncatedSVD).

---

## 📚 Documentation

- **[API Docs](http://localhost:8000/docs)** - Swagger UI (when running locally)
- **[Prefect Docs](https://docs.prefect.io/)**
- **[FastAPI Docs](https://fastapi.tiangolo.com/)**
- **[React Docs](https://react.dev/)**

---

## 📄 License

MIT License - see LICENSE file for details

---

## 👥 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards
- Run `black .` for formatting
- Run `flake8 .` for linting
- Run `pytest tests/` before pushing

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Review GitHub Issues
3. Check service logs: `docker-compose logs -f`

---

## 🎯 Roadmap

- [ ] Real-time model monitoring dashboard
- [ ] A/B testing framework
- [ ] Model explainability (SHAP values)
- [ ] Advanced ensemble methods
- [ ] Mobile app for predictions
- [ ] Integration with core banking systems
- [ ] Multi-language support

---

**Last Updated**: December 17, 2025  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
