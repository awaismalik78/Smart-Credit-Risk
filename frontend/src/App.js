import React, { useState, useEffect } from 'react';
import './App.css';
import LoanPredictionForm from './pages/LoanPredictionForm';
import PredictionResults from './components/PredictionResults';
import { checkHealth } from './services/api';

function App() {
  const [apiStatus, setApiStatus] = useState('loading');
  const [predictions, setPredictions] = useState(null);

  useEffect(() => {
    checkHealth()
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('error'));
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏦 Smart Credit Risk Platform</h1>
        <p>AI-Powered Loan Prediction & Customer Segmentation</p>
      </header>

      <div className="status-indicator">
        <span className={`status ${apiStatus}`}>
          API Status: {apiStatus === 'ok' ? '✓ Connected' : apiStatus === 'loading' ? '⏳ Connecting...' : '✗ Disconnected'}
        </span>
      </div>

      <main className="container">
        <section className="form-section">
          <LoanPredictionForm onPredictionsUpdate={setPredictions} />
        </section>

        {predictions && (
          <section className="results-section">
            <PredictionResults data={predictions} />
          </section>
        )}
      </main>

      <footer>
        <p>© 2025 Smart Credit Risk Platform. ML-powered lending decisions.</p>
      </footer>
    </div>
  );
}

export default App;
