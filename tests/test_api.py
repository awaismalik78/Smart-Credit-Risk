"""
Unit tests for FastAPI endpoints.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""
    
    def test_health_status_ok(self):
        response = client.get('/health')
        assert response.status_code == 200
        data = response.json()
        assert data == {"status": "ok"}


class TestPredictionEndpoints:
    """Test prediction endpoints."""
    
    sample_input = {
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
    
    def test_classification_endpoint(self):
        """Test loan approval prediction endpoint."""
        response = client.post('/predict/classification', json=self.sample_input)
        assert response.status_code == 200
        data = response.json()
        assert "loan_status" in data
        assert "probability" in data
    
    def test_regression_endpoint(self):
        """Test loan amount prediction endpoint."""
        response = client.post('/predict/regression', json=self.sample_input)
        assert response.status_code == 200
        data = response.json()
        assert "predicted_value" in data
        assert isinstance(data["predicted_value"], (int, float))
    
    def test_segmentation_endpoint(self):
        """Test customer segmentation endpoint."""
        response = client.post('/segment/customer', json=self.sample_input)
        assert response.status_code == 200
        data = response.json()
        assert "cluster" in data
        assert isinstance(data["cluster"], int)


class TestErrorHandling:
    """Test API error handling."""
    
    def test_classification_missing_field(self):
        """Test classification with missing required field."""
        incomplete_input = {"loan_amount": 5000}
        response = client.post('/predict/classification', json=incomplete_input)
        assert response.status_code == 422  # Unprocessable entity
    
    def test_regression_missing_field(self):
        """Test regression with missing required field."""
        incomplete_input = {"loan_amount": 5000}
        response = client.post('/predict/regression', json=incomplete_input)
        assert response.status_code == 422

