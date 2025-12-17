import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const predictClassification = (loanData) => {
  return api.post('/predict/classification', loanData);
};

export const predictRegression = (loanData) => {
  return api.post('/predict/regression', loanData);
};

export const segmentCustomer = (loanData) => {
  return api.post('/segment/customer', loanData);
};

export const checkHealth = () => {
  return api.get('/health');
};

export default api;
