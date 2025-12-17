import React, { useState } from 'react';
import { predictClassification, predictRegression, segmentCustomer } from '../services/api';

const LoanPredictionForm = ({ onPredictionsUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    loan_amount: 5000,
    interest_rate: 5.5,
    loan_status: 'approved',
    income: 50000,
    employment_length: 5,
    purpose: 'debt_consolidation',
    term: 36,
    credit_score: 700,
    monthly_debt: 1000,
    years_of_credit_history: 10,
  });

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: isNaN(value) ? value : parseFloat(value)
    }));
  };

  const handleReset = () => {
    setFormData({
      loan_amount: 5000,
      interest_rate: 5.5,
      loan_status: 'approved',
      income: 50000,
      employment_length: 5,
      purpose: 'debt_consolidation',
      term: 36,
      credit_score: 700,
      monthly_debt: 1000,
      years_of_credit_history: 10,
    });
    setError(null);
    onPredictionsUpdate(null);
  };

  const handlePredict = async () => {
    setLoading(true);
    setError(null);

    try {
      // Convert employment_length and term to strings for API
      const payload = {
        ...formData,
        employment_length: String(formData.employment_length),
        term: String(formData.term)
      };

      const [classRes, regRes, segRes] = await Promise.all([
        predictClassification(payload),
        predictRegression(payload),
        segmentCustomer(payload)
      ]);

      onPredictionsUpdate({
        classification: classRes.data,
        regression: regRes.data,
        segmentation: segRes.data,
        formData
      });
    } catch (err) {
      let errorMessage = 'Error making predictions';
      
      // Handle Pydantic validation errors
      if (err.response?.data?.detail) {
        const detail = err.response.data.detail;
        if (Array.isArray(detail)) {
          // Pydantic validation errors are arrays
          errorMessage = detail.map(d => 
            typeof d === 'object' ? `${d.msg} at ${d.loc?.join('.')}` : String(d)
          ).join('; ');
        } else if (typeof detail === 'object') {
          errorMessage = JSON.stringify(detail);
        } else {
          errorMessage = String(detail);
        }
      } else if (err.response?.data) {
        // Handle other error responses
        errorMessage = typeof err.response.data === 'string' ? err.response.data : JSON.stringify(err.response.data);
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>📋 Loan Details</h2>
      
      {error && <div className="error-message">{error}</div>}

      <div className="form-group">
        <label>Loan Amount ($)</label>
        <input 
          type="number" 
          name="loan_amount" 
          value={formData.loan_amount}
          onChange={handleInputChange}
          min="1000"
          step="100"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Interest Rate (%)</label>
          <input 
            type="number" 
            name="interest_rate" 
            value={formData.interest_rate}
            onChange={handleInputChange}
            min="0"
            step="0.1"
          />
        </div>
        <div className="form-group">
          <label>Loan Term (months)</label>
          <input 
            type="number" 
            name="term" 
            value={formData.term}
            onChange={handleInputChange}
            min="6"
            step="6"
          />
        </div>
      </div>

      <div className="form-group">
        <label>Annual Income ($)</label>
        <input 
          type="number" 
          name="income" 
          value={formData.income}
          onChange={handleInputChange}
          min="10000"
          step="5000"
        />
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Employment Length (years)</label>
          <input 
            type="number" 
            name="employment_length" 
            value={formData.employment_length}
            onChange={handleInputChange}
            min="0"
            step="1"
          />
        </div>
        <div className="form-group">
          <label>Credit Score</label>
          <input 
            type="number" 
            name="credit_score" 
            value={formData.credit_score}
            onChange={handleInputChange}
            min="300"
            max="850"
            step="10"
          />
        </div>
      </div>

      <div className="form-row">
        <div className="form-group">
          <label>Monthly Debt ($)</label>
          <input 
            type="number" 
            name="monthly_debt" 
            value={formData.monthly_debt}
            onChange={handleInputChange}
            min="0"
            step="100"
          />
        </div>
        <div className="form-group">
          <label>Years of Credit History</label>
          <input 
            type="number" 
            name="years_of_credit_history" 
            value={formData.years_of_credit_history}
            onChange={handleInputChange}
            min="0"
            step="1"
          />
        </div>
      </div>

      <div className="form-group">
        <label>Loan Purpose</label>
        <select 
          name="purpose" 
          value={formData.purpose}
          onChange={handleInputChange}
        >
          <option value="debt_consolidation">Debt Consolidation</option>
          <option value="home_improvement">Home Improvement</option>
          <option value="credit_card">Credit Card</option>
          <option value="personal">Personal</option>
          <option value="auto">Auto</option>
          <option value="business">Business</option>
          <option value="other">Other</option>
        </select>
      </div>

      <div className="form-group">
        <label>Loan Status</label>
        <select 
          name="loan_status" 
          value={formData.loan_status}
          onChange={handleInputChange}
        >
          <option value="approved">Approved</option>
          <option value="rejected">Rejected</option>
          <option value="pending">Pending</option>
        </select>
      </div>

      <div className="button-group">
        <button 
          className="btn-predict" 
          onClick={handlePredict}
          disabled={loading}
        >
          {loading ? '⏳ Predicting...' : '🔮 Get Prediction'}
        </button>
        <button 
          className="btn-reset" 
          onClick={handleReset}
          disabled={loading}
        >
          ↻ Reset
        </button>
      </div>
    </div>
  );
};

export default LoanPredictionForm;
