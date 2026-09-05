import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Analytics
export const getAnalyticsOverview = async () => {
  const response = await api.get('/api/v1/analytics/overview');
  return response.data;
};

export const getRecoveryRate = async (days: number = 30) => {
  const response = await api.get(`/api/v1/analytics/recovery-rate?days=${days}`);
  return response.data;
};

export const getInterventionEffectiveness = async () => {
  const response = await api.get('/api/v1/analytics/intervention-effectiveness');
  return response.data;
};

export const getRevenueSaved = async (days: number = 30) => {
  const response = await api.get(`/api/v1/analytics/revenue-saved?days=${days}`);
  return response.data;
};

// Risks
export const getRisks = async (params?: {
  status?: string;
  risk_type?: string;
  priority?: string;
  limit?: number;
  offset?: number;
}) => {
  const response = await api.get('/api/v1/risks', { params });
  return response.data;
};

export const getRisk = async (id: string) => {
  const response = await api.get(`/api/v1/risks/${id}`);
  return response.data;
};

export const detectRisks = async () => {
  const response = await api.post('/api/v1/risks/detect');
  return response.data;
};

export const processRisk = async (id: string) => {
  const response = await api.post(`/api/v1/risks/${id}/process`);
  return response.data;
};

export const getRiskStats = async () => {
  const response = await api.get('/api/v1/risks/stats/overview');
  return response.data;
};

// Interventions
export const getInterventions = async (params?: {
  status?: string;
  limit?: number;
  offset?: number;
}) => {
  const response = await api.get('/api/v1/interventions', { params });
  return response.data;
};

export const getIntervention = async (id: string) => {
  const response = await api.get(`/api/v1/interventions/${id}`);
  return response.data;
};

export const executeIntervention = async (id: string) => {
  const response = await api.post(`/api/v1/interventions/${id}/execute`);
  return response.data;
};

// AI
export const analyzeRisk = async (riskId: string) => {
  const response = await api.post('/api/v1/ai/analyze', { risk_id: riskId });
  return response.data;
};

export const getAuditTrail = async (entityId: string, entityType: string = 'risk') => {
  const response = await api.get(`/api/v1/ai/audit-trail/${entityId}?entity_type=${entityType}`);
  return response.data;
};
