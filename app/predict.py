import joblib
from pathlib import Path
import pandas as pd
import numpy as np
from scipy import sparse
import logging

logger = logging.getLogger(__name__)
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"

classification_model = None
regression_model = None
clustering_model = None
preprocessor = None
preprocessor_config = None
svd = None


def load_models():
    global classification_model, regression_model, clustering_model, preprocessor, preprocessor_config, svd
    try:
        preproc_path = MODELS_DIR / 'preprocessor.joblib'
        if preproc_path.exists():
            preprocessor = joblib.load(preproc_path)
            logger.info('Loaded preprocessor')
    except Exception as e:
        logger.warning('Preprocessor not loaded: %s', e)
        preprocessor = None

    try:
        config_path = MODELS_DIR / 'preprocessor_config.joblib'
        if config_path.exists():
            preprocessor_config = joblib.load(config_path)
            logger.info('Loaded preprocessor config')
    except Exception as e:
        logger.info('No preprocessor config: %s', e)
        preprocessor_config = None

    try:
        svd_path = MODELS_DIR / 'svd_transformer.joblib'
        if svd_path.exists():
            svd = joblib.load(svd_path)
            logger.info('Loaded svd transformer')
    except Exception as e:
        logger.info('No svd transformer: %s', e)
        svd = None

    try:
        p = MODELS_DIR / 'classification_model.pkl'
        if p.exists():
            classification_model = joblib.load(p)
            logger.info('Loaded classification model')
    except Exception as e:
        logger.warning('Could not load classification model: %s', e)
        classification_model = None

    try:
        p = MODELS_DIR / 'regression_model.pkl'
        if p.exists():
            regression_model = joblib.load(p)
            logger.info('Loaded regression model')
    except Exception as e:
        logger.warning('Could not load regression model: %s', e)
        regression_model = None

    try:
        p = MODELS_DIR / 'clustering_model.pkl'
        if p.exists():
            clustering_model = joblib.load(p)
            logger.info('Loaded clustering model')
    except Exception as e:
        logger.warning('Could not load clustering model: %s', e)
        clustering_model = None


def _prepare_features(input_dict: dict):
    # Build a one-row DataFrame and transform with preprocessor; handle sparse output
    if preprocessor is None:
        raise RuntimeError('Preprocessor not loaded')
    
    # Fill missing columns with sensible defaults from config
    filled_dict = input_dict.copy()
    
    # Get all expected columns from config
    if preprocessor_config and 'all_cols' in preprocessor_config:
        expected_cols = preprocessor_config['all_cols']
        numeric_cols = preprocessor_config.get('numeric_cols', [])
        categorical_cols = preprocessor_config.get('categorical_cols', [])
        
        # Fill missing columns with defaults
        for col in expected_cols:
            if col not in filled_dict:
                if col in numeric_cols:
                    filled_dict[col] = 0  # Default numeric value
                elif col in categorical_cols:
                    filled_dict[col] = 'missing'  # Default categorical value
                else:
                    # Default for any other column
                    if col.lower() in ['loan_status', 'loan amount', 'interest_rate']:
                        filled_dict[col] = 0 if 'amount' in col.lower() or 'rate' in col.lower() else 'approved'
                    else:
                        filled_dict[col] = 0
    
    df = pd.DataFrame([filled_dict])
    X = preprocessor.transform(df)
    # If SVD exists and X is sparse or high-dim, apply it
    if svd is not None:
        if sparse.issparse(X):
            X = X
        X_reduced = svd.transform(X)
        return np.asarray(X_reduced)
    # ensure dense array for sklearn estimators
    if sparse.issparse(X):
        X = X.toarray()
    return np.asarray(X)


def predict_classification(input_dict: dict):
    if classification_model is None:
        raise RuntimeError('Classification model not loaded')
    X = _prepare_features(input_dict)
    # sklearn expects 2D
    proba = None
    try:
        if hasattr(classification_model, 'predict_proba'):
            proba = classification_model.predict_proba(X)[0]
            idx = int(np.argmax(proba))
            label = classification_model.classes_[idx]
            return {'loan_status': str(label), 'probability': float(proba[idx])}
        else:
            pred = classification_model.predict(X)[0]
            return {'loan_status': str(pred), 'probability': None}
    except Exception as e:
        logger.error('Classification prediction error: %s', e)
        raise


def predict_regression(input_dict: dict):
    if regression_model is None:
        raise RuntimeError('Regression model not loaded')
    X = _prepare_features(input_dict)
    try:
        return float(regression_model.predict(X)[0])
    except Exception as e:
        logger.error('Regression prediction error: %s', e)
        raise


def predict_cluster(input_dict: dict):
    if clustering_model is None:
        raise RuntimeError('Clustering model not loaded')
    X = _prepare_features(input_dict)
    try:
        return int(clustering_model.predict(X)[0])
    except Exception as e:
        logger.error('Clustering prediction error: %s', e)
        raise
