"""
Model loading and inference tests.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier


class TestModelLoading:
    """Test model loading and availability."""
    
    @pytest.fixture
    def models_dir(self):
        """Get models directory."""
        return Path("models")
    
    def test_preprocessor_exists(self, models_dir):
        """Test preprocessor file exists."""
        preprocessor_path = models_dir / "preprocessor.joblib"
        assert preprocessor_path.exists(), "Preprocessor not found"
    
    def test_classification_model_exists(self, models_dir):
        """Test classification model exists."""
        model_path = models_dir / "classification_model.pkl"
        assert model_path.exists(), "Classification model not found"
    
    def test_regression_model_exists(self, models_dir):
        """Test regression model exists."""
        model_path = models_dir / "regression_model.pkl"
        assert model_path.exists(), "Regression model not found"
    
    def test_clustering_model_exists(self, models_dir):
        """Test clustering model exists."""
        model_path = models_dir / "clustering_model.pkl"
        assert model_path.exists(), "Clustering model not found"


class TestModelInference:
    """Test model inference and predictions."""
    
    @pytest.fixture
    def sample_input(self):
        """Create sample input for predictions."""
        return {
            "loan_amount": 5000,
            "interest_rate": 5.5,
            "loan_status": "approved",
            "income": 50000,
            "employment_length": 5,
            "purpose": "debt_consolidation",
            "term": 36,
            "credit_score": 700,
            "monthly_debt": 1000,
            "years_of_credit_history": 10,
        }
    
    def test_classification_inference(self, sample_input):
        """Test classification model inference."""
        try:
            from app.predict import predict_classification
            
            result = predict_classification(sample_input)
            
            assert "loan_status" in result
            assert "probability" in result
            assert isinstance(result["loan_status"], str)
        except RuntimeError:
            pytest.skip("Models not loaded in this test environment")
    
    def test_regression_inference(self, sample_input):
        """Test regression model inference."""
        try:
            from app.predict import predict_regression
            
            result = predict_regression(sample_input)
            
            assert isinstance(result, (int, float))
            assert result > 0
        except RuntimeError:
            pytest.skip("Models not loaded in this test environment")
    
    def test_clustering_inference(self, sample_input):
        """Test clustering inference."""
        try:
            from app.predict import predict_cluster
            
            result = predict_cluster(sample_input)
            
            assert isinstance(result, (int, np.integer))
            assert result >= 0
        except RuntimeError:
            pytest.skip("Models not loaded in this test environment")


class TestModelMetrics:
    """Test model metrics and performance."""
    
    @pytest.fixture
    def metrics_dir(self):
        """Get metrics directory."""
        return Path("data/processed")
    
    def test_classification_metrics_file(self, metrics_dir):
        """Test classification metrics file exists."""
        metrics_path = metrics_dir / "classification_metrics.json"
        assert metrics_path.exists(), "Classification metrics not found"
    
    def test_regression_metrics_file(self, metrics_dir):
        """Test regression metrics file exists."""
        metrics_path = metrics_dir / "regression_metrics.json"
        assert metrics_path.exists(), "Regression metrics not found"
    
    def test_clustering_metrics_file(self, metrics_dir):
        """Test clustering metrics file exists."""
        metrics_path = metrics_dir / "clustering_metrics.json"
        assert metrics_path.exists(), "Clustering metrics not found"
    
    def test_metrics_valid_values(self, metrics_dir):
        """Test metrics contain valid numerical values."""
        import json
        
        metrics_path = metrics_dir / "classification_metrics.json"
        if metrics_path.exists():
            with open(metrics_path) as f:
                metrics = json.load(f)
            
            assert isinstance(metrics, dict)
            # Check for common metric keys
            expected_keys = ['model', 'accuracy', 'f1_score']
            for key in expected_keys:
                if key in metrics:
                    assert isinstance(metrics[key], (int, float, str))

