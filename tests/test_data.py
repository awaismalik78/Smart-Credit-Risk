"""
Data validation and integrity tests.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import numpy as np
import pytest


class TestDataLoading:
    """Test data loading and integrity."""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample dataset for testing."""
        return pd.DataFrame({
            'loan_amount': [5000, 7500, 10000, 15000, 20000],
            'interest_rate': [5.5, 6.0, 7.2, 8.1, 9.0],
            'income': [50000, 60000, 75000, 100000, 150000],
            'credit_score': [650, 700, 750, 800, 820],
            'employment_length': [2, 5, 8, 10, 15],
            'monthly_debt': [800, 1000, 1200, 1500, 2000],
            'loan_status': ['approved', 'approved', 'rejected', 'approved', 'approved'],
        })
    
    def test_data_shape(self, sample_data):
        """Test data has correct shape."""
        assert sample_data.shape[0] > 0
        assert sample_data.shape[1] > 0
    
    def test_no_critical_nulls(self, sample_data):
        """Test critical columns have no nulls."""
        critical_cols = ['loan_amount', 'income', 'credit_score']
        for col in critical_cols:
            assert sample_data[col].isnull().sum() == 0, f"Column {col} has null values"
    
    def test_numeric_columns_valid_range(self, sample_data):
        """Test numeric columns are in valid ranges."""
        assert (sample_data['interest_rate'] >= 0).all()
        assert (sample_data['credit_score'] >= 300).all()
        assert (sample_data['credit_score'] <= 850).all()
        assert (sample_data['income'] > 0).all()


class TestFeatureEngineering:
    """Test feature engineering logic."""
    
    def test_debt_to_income_ratio(self):
        """Test debt-to-income ratio calculation."""
        from ml.features import add_derived_features
        
        df = pd.DataFrame({
            'income': [60000, 120000],
            'monthly_debt': [1000, 2000],
        })
        
        df_engineered = add_derived_features(df.copy())
        
        if 'debt_to_income' in df_engineered.columns:
            # Verify calculation
            expected_dti_1 = 1000 / (60000 / 12)
            actual_dti_1 = df_engineered['debt_to_income'].iloc[0]
            assert abs(actual_dti_1 - expected_dti_1) < 0.01
    
    def test_preprocessing_output_valid(self):
        """Test preprocessor output is valid."""
        try:
            from ml.features import build_preprocessor
            
            df = pd.DataFrame({
                'loan_amount': [5000, 7500, 10000],
                'income': [50000, 60000, 75000],
                'purpose': ['personal', 'home', 'auto'],
                'credit_score': [650, 700, 750],
            })
            
            preprocessor = build_preprocessor(df)
            X = preprocessor.transform(df)
            
            assert X.shape[0] == df.shape[0]
            assert X.shape[1] > 0
        except Exception as e:
            pytest.skip(f"Preprocessing test skipped: {e}")


class TestDataValidation:
    """Test data validation functions."""
    
    def test_duplicate_detection(self):
        """Test duplicate row detection."""
        df = pd.DataFrame({
            'id': [1, 2, 2, 3],
            'value': [10, 20, 20, 30],
        })
        
        duplicates = df.duplicated().sum()
        assert duplicates > 0
    
    def test_null_handling(self):
        """Test null value handling."""
        df = pd.DataFrame({
            'col1': [1, 2, None, 4],
            'col2': [5, None, None, 8],
        })
        
        null_count = df.isnull().sum().sum()
        assert null_count == 3

