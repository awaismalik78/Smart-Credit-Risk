"""Evaluation utilities: compute and log evaluation metrics for models."""
import json
from pathlib import Path
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, mean_squared_error, mean_absolute_error, r2_score, silhouette_score


def log_metrics(path, metrics: dict):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(metrics, f, indent=2)


def classification_metrics(y_true, y_pred):
    return {
        'accuracy': float(accuracy_score(y_true, y_pred)),
        # use macro F1 to be robust to string labels and both binary/multi-class
        'f1': float(f1_score(y_true, y_pred, average='macro'))
    }


def regression_metrics(y_true, y_pred):
    return {
        'rmse': float(np.sqrt(mean_squared_error(y_true, y_pred))),
        'mae': float(mean_absolute_error(y_true, y_pred)),
        'r2': float(r2_score(y_true, y_pred))
    }


def clustering_metrics(X, labels):
    try:
        s = float(silhouette_score(X, labels))
    except Exception:
        s = None
    return {'silhouette': s}
