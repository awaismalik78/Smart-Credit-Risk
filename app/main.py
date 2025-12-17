from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging

from .schemas import LoanInput, ClassificationResponse, RegressionResponse, ClusterResponse
from . import predict as predictor

logger = logging.getLogger("uvicorn.error")

app = FastAPI(title="Smart Credit Risk Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    logger.info('Loading ML models on startup')
    try:
        predictor.load_models()
    except Exception as e:
        logger.exception('Error loading models: %s', e)


@app.get('/health')
def health():
    return {"status": "ok"}


@app.post('/predict/classification', response_model=ClassificationResponse)
def predict_classification(input: LoanInput):
    try:
        res = predictor.predict_classification(input.dict())
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/predict/regression', response_model=RegressionResponse)
def predict_regression(input: LoanInput):
    try:
        val = predictor.predict_regression(input.dict())
        return {"predicted_value": val}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post('/segment/customer', response_model=ClusterResponse)
def segment_customer(input: LoanInput):
    try:
        c = predictor.predict_cluster(input.dict())
        return {"cluster": c}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
