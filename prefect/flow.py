"""
Prefect workflow for Smart Credit Risk Platform ML Pipeline.
Orchestrates data ingestion, preprocessing, training, and evaluation.
"""

from prefect import flow, task, get_run_logger
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ml.eda import summarise, save_histograms
from ml.features import add_derived_features, build_preprocessor
from ml.prepare_data import prepare_datasets
from ml.train import train_classification, train_regression, train_pca_and_clustering, run_all
from ml.evaluate import classification_metrics, regression_metrics, clustering_metrics
import pandas as pd
import joblib


@task(retries=2, retry_delay_seconds=5)
def ingest_data(data_path: str = "data/bank_loan.csv"):
    """Ingest dataset from CSV file."""
    logger = get_run_logger()
    logger.info(f"Ingesting data from {data_path}")
    
    try:
        df = pd.read_csv(data_path)
        logger.info(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
        return df
    except Exception as e:
        logger.error(f"Failed to ingest data: {e}")
        raise


@task(retries=1, retry_delay_seconds=5)
def validate_data(df: pd.DataFrame) -> bool:
    """Validate data quality and integrity."""
    logger = get_run_logger()
    logger.info("Validating data quality...")
    
    try:
        # Check for nulls
        null_count = df.isnull().sum().sum()
        logger.info(f"  - Total null values: {null_count}")
        
        # Check dtypes
        logger.info(f"  - Data types: {df.dtypes.nunique()} unique types")
        
        # Check dimensions
        if df.shape[0] == 0 or df.shape[1] == 0:
            raise ValueError("DataFrame is empty")
        
        logger.info("✓ Data validation passed")
        return True
    except Exception as e:
        logger.error(f"Data validation failed: {e}")
        raise


@task
def perform_eda(df: pd.DataFrame) -> dict:
    """Perform exploratory data analysis."""
    logger = get_run_logger()
    logger.info("Performing EDA...")
    
    try:
        # Summarize
        summary = summarise(df)
        logger.info(f"✓ EDA summary generated: {len(summary)} metrics")
        
        # Save histograms
        save_histograms(df)
        logger.info("✓ Histograms saved")
        
        return summary
    except Exception as e:
        logger.error(f"EDA failed: {e}")
        raise


@task
def feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived features."""
    logger = get_run_logger()
    logger.info("Performing feature engineering...")
    
    try:
        df_engineered = add_derived_features(df.copy())
        logger.info(f"✓ Added derived features: {df_engineered.shape[1]} total columns")
        return df_engineered
    except Exception as e:
        logger.error(f"Feature engineering failed: {e}")
        raise


@task
def preprocess_and_prepare(df: pd.DataFrame):
    """Build preprocessor and prepare datasets for training."""
    logger = get_run_logger()
    logger.info("Building preprocessor and preparing data...")
    
    try:
        # Prepare datasets (this handles normalization, encoding, etc.)
        prepare_datasets(df)
        logger.info("✓ Data preparation complete")
        
        # Load prepared datasets
        class_df = pd.read_csv("data/processed/for_classification.csv")
        reg_df = pd.read_csv("data/processed/for_regression.csv")
        
        logger.info(f"  - Classification data: {class_df.shape}")
        logger.info(f"  - Regression data: {reg_df.shape}")
        
        return {"classification": class_df, "regression": reg_df}
    except Exception as e:
        logger.error(f"Preprocessing failed: {e}")
        raise


@task
def train_models():
    """Train all ML models: classification, regression, clustering."""
    logger = get_run_logger()
    logger.info("Training ML models...")
    
    try:
        run_all()
        logger.info("✓ Model training complete")
        
        # Load and log model info
        models_dir = Path("models")
        models = {
            "classification": models_dir / "classification_model.pkl",
            "regression": models_dir / "regression_model.pkl",
            "clustering": models_dir / "clustering_model.pkl",
            "pca": models_dir / "pca_model.pkl",
        }
        
        for name, path in models.items():
            if path.exists():
                logger.info(f"  - {name}: {path.stat().st_size / 1024:.1f} KB")
        
        return True
    except Exception as e:
        logger.error(f"Model training failed: {e}")
        raise


@task
def evaluate_models():
    """Load and log model metrics."""
    logger = get_run_logger()
    logger.info("Evaluating models...")
    
    try:
        metrics_files = {
            "classification": "data/processed/classification_metrics.json",
            "regression": "data/processed/regression_metrics.json",
            "clustering": "data/processed/clustering_metrics.json",
        }
        
        all_metrics = {}
        for name, path in metrics_files.items():
            if Path(path).exists():
                with open(path) as f:
                    metrics = json.load(f)
                    all_metrics[name] = metrics
                    logger.info(f"✓ {name}: {metrics}")
        
        return all_metrics
    except Exception as e:
        logger.error(f"Model evaluation failed: {e}")
        raise


@task
def notify_completion(status: str):
    """Notify completion of pipeline."""
    logger = get_run_logger()
    logger.info(f"Pipeline Status: {status}")
    logger.info("=" * 60)
    logger.info("ML Pipeline Execution Complete!")
    logger.info("=" * 60)
    return status


@flow(name="smart-credit-risk-ml-pipeline", description="End-to-end ML pipeline for credit risk prediction")
def ml_pipeline():
    """
    Main ML pipeline flow orchestrating all stages:
    1. Data Ingestion
    2. Data Validation
    3. EDA
    4. Feature Engineering
    5. Data Preprocessing
    6. Model Training
    7. Model Evaluation
    8. Notification
    """
    logger = get_run_logger()
    logger.info("Starting Smart Credit Risk ML Pipeline")
    logger.info("=" * 60)
    
    try:
        # Stage 1: Ingest Data
        df = ingest_data()
        
        # Stage 2: Validate Data
        validate_data(df)
        
        # Stage 3: EDA
        perform_eda(df)
        
        # Stage 4: Feature Engineering
        df_engineered = feature_engineering(df)
        
        # Stage 5: Preprocess & Prepare
        preprocess_and_prepare(df_engineered)
        
        # Stage 6: Train Models
        train_models()
        
        # Stage 7: Evaluate Models
        metrics = evaluate_models()
        
        # Stage 8: Notify Completion
        notify_completion("SUCCESS ✓")
        
        return {"status": "success", "metrics": metrics}
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        notify_completion(f"FAILED: {str(e)}")
        raise


@flow(name="daily-model-training", description="Scheduled daily model retraining")
def daily_training_flow():
    """Daily retraining flow for model updates."""
    logger = get_run_logger()
    logger.info("Starting daily model retraining...")
    ml_pipeline()


if __name__ == "__main__":
    ml_pipeline()
