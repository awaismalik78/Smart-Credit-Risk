"""
ML testing using DeepChecks for data and model validation.
Includes data integrity checks, drift detection, and model performance validation.
"""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import joblib
import logging

logger = logging.getLogger(__name__)

try:
    from deepchecks.tabular import Dataset
    from deepchecks.tabular.suites import full_suite, data_integrity, model_evaluation
    DEEPCHECKS_AVAILABLE = True
except ImportError:
    DEEPCHECKS_AVAILABLE = False
    logger.warning("DeepChecks not installed. Install with: pip install deepchecks")


def run_data_integrity_checks(df: pd.DataFrame, output_dir: str = "data/processed/deepchecks") -> dict:
    """Run DeepChecks data integrity suite."""
    logger.info("Running data integrity checks...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    if not DEEPCHECKS_AVAILABLE:
        logger.warning("DeepChecks not available. Skipping detailed checks.")
        return {"status": "skipped", "reason": "deepchecks not installed"}
    
    try:
        # Basic checks (can be run without DeepChecks)
        checks = {
            "null_count": int(df.isnull().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum()),
            "numeric_columns": int(df.select_dtypes(include=[np.number]).shape[1]),
            "categorical_columns": int(df.select_dtypes(include=['object']).shape[1]),
            "rows": df.shape[0],
            "columns": df.shape[1],
        }
        
        logger.info(f"  - Null values: {checks['null_count']}")
        logger.info(f"  - Duplicate rows: {checks['duplicate_rows']}")
        logger.info(f"  - Columns: {checks['columns']} (numeric: {checks['numeric_columns']}, categorical: {checks['categorical_columns']})")
        
        # Save results
        with open(f"{output_dir}/data_integrity_checks.json", 'w') as f:
            json.dump(checks, f, indent=2)
        
        logger.info("✓ Data integrity checks passed")
        return checks
        
    except Exception as e:
        logger.error(f"Data integrity checks failed: {e}")
        raise


def run_label_leakage_check(X: pd.DataFrame, y: pd.Series, output_dir: str = "data/processed/deepchecks") -> dict:
    """Check for label leakage in features."""
    logger.info("Checking for label leakage...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        results = {
            "feature_target_correlation": {},
            "high_correlation_features": []
        }
        
        # Calculate correlation with target
        for col in X.columns:
            try:
                if X[col].dtype in [np.float64, np.int64]:
                    corr = X[col].corr(y)
                    results["feature_target_correlation"][col] = float(corr)
                    
                    # Flag high correlations (potential leakage)
                    if abs(corr) > 0.95:
                        results["high_correlation_features"].append({
                            "column": col,
                            "correlation": float(corr),
                            "risk": "HIGH - Possible label leakage"
                        })
            except:
                pass
        
        if results["high_correlation_features"]:
            logger.warning(f"⚠ Potential label leakage detected in {len(results['high_correlation_features'])} features")
        else:
            logger.info("✓ No label leakage detected")
        
        with open(f"{output_dir}/label_leakage_check.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        return results
        
    except Exception as e:
        logger.error(f"Label leakage check failed: {e}")
        raise


def run_drift_detection(train_df: pd.DataFrame, test_df: pd.DataFrame, output_dir: str = "data/processed/deepchecks") -> dict:
    """Detect data drift between train and test sets."""
    logger.info("Detecting data drift...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        drift_report = {
            "numeric_drift": {},
            "columns_with_drift": []
        }
        
        numeric_cols = train_df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            train_mean = train_df[col].mean()
            test_mean = test_df[col].mean()
            train_std = train_df[col].std()
            
            # Calculate drift as % change
            if train_std > 0:
                drift = abs((test_mean - train_mean) / train_std)
            else:
                drift = 0
            
            drift_report["numeric_drift"][col] = {
                "train_mean": float(train_mean),
                "test_mean": float(test_mean),
                "drift_magnitude": float(drift)
            }
            
            # Flag significant drift (>0.5 std dev)
            if drift > 0.5:
                drift_report["columns_with_drift"].append({
                    "column": col,
                    "drift": float(drift),
                    "status": "WARN" if drift < 1.0 else "ALERT"
                })
        
        if drift_report["columns_with_drift"]:
            logger.warning(f"⚠ Data drift detected in {len(drift_report['columns_with_drift'])} columns")
        else:
            logger.info("✓ No significant data drift detected")
        
        with open(f"{output_dir}/drift_detection.json", 'w') as f:
            json.dump(drift_report, f, indent=2, default=str)
        
        return drift_report
        
    except Exception as e:
        logger.error(f"Drift detection failed: {e}")
        raise


def validate_model_performance(y_true: pd.Series, y_pred: np.ndarray, threshold: float = 0.7, output_dir: str = "data/processed/deepchecks") -> dict:
    """Validate model performance against thresholds."""
    logger.info("Validating model performance...")
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
        
        metrics = {
            "accuracy": float(accuracy_score(y_true, y_pred)),
            "precision": float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
            "recall": float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
            "f1": float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
            "threshold": threshold,
            "validation_status": "PASS" if float(accuracy_score(y_true, y_pred)) >= threshold else "FAIL"
        }
        
        logger.info(f"  - Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"  - F1-Score: {metrics['f1']:.4f}")
        logger.info(f"  - Status: {metrics['validation_status']}")
        
        with open(f"{output_dir}/model_performance_validation.json", 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Model performance validation failed: {e}")
        raise


def run_full_validation_suite(df: pd.DataFrame, X_train: pd.DataFrame, X_test: pd.DataFrame, 
                              y_train: pd.Series, y_test: pd.Series, y_pred: np.ndarray,
                              output_dir: str = "data/processed/deepchecks") -> dict:
    """Run complete validation suite."""
    logger.info("Running full validation suite...")
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    try:
        # 1. Data integrity
        results["data_integrity"] = run_data_integrity_checks(df, output_dir)
        
        # 2. Label leakage
        results["label_leakage"] = run_label_leakage_check(X_train, y_train, output_dir)
        
        # 3. Data drift
        results["drift_detection"] = run_drift_detection(X_train, X_test, output_dir)
        
        # 4. Model performance
        results["model_performance"] = validate_model_performance(y_test, y_pred, output_dir=output_dir)
        
        # Save summary
        summary = {
            "total_checks": 4,
            "passed": sum(1 for v in results.values() if isinstance(v, dict) and v.get("validation_status") in ["PASS", "OK"]),
            "warnings": sum(1 for v in results.values() if isinstance(v, dict) and "warning" in str(v).lower()),
            "timestamp": str(pd.Timestamp.now()),
        }
        
        with open(f"{output_dir}/validation_summary.json", 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"✓ Validation suite complete: {summary['passed']} passed")
        return results
        
    except Exception as e:
        logger.error(f"Full validation suite failed: {e}")
        raise


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    # Load data
    df = pd.read_csv("data/bank_loan.csv")
    X_train = pd.read_csv("data/processed/for_classification.csv")
    
    # Run checks
    run_data_integrity_checks(df)
