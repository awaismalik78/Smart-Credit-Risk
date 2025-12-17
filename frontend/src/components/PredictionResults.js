import React from 'react';
import { Pie, Bar, Scatter } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  ArcElement,
  BarElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  BarElement,
  ArcElement,
  Tooltip,
  Legend,
  Title
);

const PredictionResults = ({ data }) => {
  if (!data) return null;

  const { classification, regression, segmentation, formData } = data;

  const getRiskColor = (status) => {
    const statusStr = String(status).toLowerCase();
    if (statusStr.includes('approved') || statusStr === '0') return 'risk-low';
    if (statusStr.includes('pending')) return 'risk-medium';
    return 'risk-high';
  };

  const getSegmentLabel = (cluster) => {
    const labels = {
      0: 'Low Risk 🟢',
      1: 'Medium Risk 🟡',
      2: 'High Risk 🔴'
    };
    return labels[cluster] || `Cluster ${cluster}`;
  };

  // Pie chart for loan status distribution
  const statusChartData = {
    labels: ['Approved', 'Rejected', 'Pending'],
    datasets: [{
      data: [60, 25, 15],
      backgroundColor: ['#4caf50', '#f44336', '#ff9800'],
      borderColor: '#fff',
      borderWidth: 2,
    }],
  };

  // Bar chart for risk factors
  const riskChartData = {
    labels: ['Debt-to-Income', 'Credit Score', 'Employment', 'Interest Rate'],
    datasets: [{
      label: 'Risk Score',
      data: [65, 75, 45, 55],
      backgroundColor: '#667eea',
      borderColor: '#667eea',
      borderWidth: 1,
    }],
  };

  return (
    <div>
      <h2>📊 Prediction Results</h2>

      {/* Classification Results */}
      <div className="results-card">
        <h3>🎯 Loan Approval Prediction</h3>
        <div className="result-item">
          <span className="result-label">Predicted Status</span>
          <span className={`result-value ${getRiskColor(classification.loan_status)}`}>
            {classification.loan_status}
          </span>
        </div>
        <div className="result-item">
          <span className="result-label">Confidence Score</span>
          <span className="result-value">
            {classification.probability ? (classification.probability * 100).toFixed(2) : 'N/A'}%
          </span>
        </div>
      </div>

      {/* Regression Results */}
      <div className="results-card">
        <h3>💰 Financial Predictions</h3>
        <div className="result-item">
          <span className="result-label">Predicted Loan Amount</span>
          <span className="result-value">${regression.predicted_value?.toFixed(2) || '0.00'}</span>
        </div>
        <div className="result-item">
          <span className="result-label">Input Loan Amount</span>
          <span className="result-value">${formData.loan_amount.toFixed(2)}</span>
        </div>
        <div className="result-item">
          <span className="result-label">Interest Rate</span>
          <span className="result-value">{formData.interest_rate}%</span>
        </div>
      </div>

      {/* Segmentation Results */}
      <div className="results-card">
        <h3>📈 Customer Segmentation</h3>
        <div className="result-item">
          <span className="result-label">Risk Segment</span>
          <span className="result-value">
            {getSegmentLabel(segmentation.cluster)}
          </span>
        </div>
        <div className="result-item">
          <span className="result-label">Cluster ID</span>
          <span className="result-value">{segmentation.cluster}</span>
        </div>
      </div>

      {/* Summary Card */}
      <div className="results-card">
        <h3>📋 Application Summary</h3>
        <div className="result-item">
          <span className="result-label">Monthly Debt</span>
          <span className="result-value">${formData.monthly_debt.toFixed(2)}</span>
        </div>
        <div className="result-item">
          <span className="result-label">Annual Income</span>
          <span className="result-value">${formData.income.toFixed(2)}</span>
        </div>
        <div className="result-item">
          <span className="result-label">Credit Score</span>
          <span className="result-value">{formData.credit_score}</span>
        </div>
        <div className="result-item">
          <span className="result-label">Employment Length</span>
          <span className="result-value">{formData.employment_length} years</span>
        </div>
      </div>

      {/* Charts */}
      <div className="chart-container">
        <h4>Loan Status Distribution</h4>
        <Pie key="status-pie" data={statusChartData} options={{ responsive: true, maintainAspectRatio: false }} />
      </div>

      <div className="chart-container">
        <h4>Risk Assessment Factors</h4>
        <Bar 
          key="risk-bar"
          data={riskChartData} 
          options={{ 
            responsive: true, 
            maintainAspectRatio: false,
            indexAxis: 'x',
            scales: {
              y: {
                beginAtZero: true,
                max: 100
              }
            }
          }} 
        />
      </div>
    </div>
  );
};

export default PredictionResults;
