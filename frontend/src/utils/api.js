import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30 seconds (AI advice takes time)
});

export const searchStocks = async (query) => {
  const res = await api.get(`/search?q=${encodeURIComponent(query)}`);
  return res.data;
};

export const getStockData = async (symbol) => {
  const res = await api.get(`/stock/${symbol}`);
  return res.data;
};

export const getChartData = async (symbol, period = '3mo') => {
  const res = await api.get(`/stock/${symbol}/chart?period=${period}`);
  return res.data;
};

export const getAnalysis = async (symbol, period = '3mo') => {
  const res = await api.get(`/analysis/${symbol}?period=${period}`);
  return res.data;
};

export const getNews = async (symbol) => {
  const res = await api.get(`/news/${symbol}`);
  return res.data;
};

export const getAdvice = async (symbol) => {
  const res = await api.get(`/advice/${symbol}`);
  return res.data;
};

export const getPeers = async (symbol) => {
  const res = await api.get(`/peers/${symbol}`);
  return res.data;
};

export const getCompanyInfo = async (symbol) => {
  const res = await api.get(`/company/${symbol}`);
  return res.data;
};

export const getInterpretation = async (symbol, period = '3mo') => {
  const res = await api.get(`/analysis/${symbol}/interpret?period=${period}`);
  return res.data;
};
export const getAlerts = async (userId) => {
  const res = await api.get(`/alerts${userId ? `?user_id=${userId}` : ''}`);
  return res.data;
};

export const createAlert = async (data) => {
  const res = await api.post('/alerts', data);
  return res.data;
};

export const deleteAlert = async (alertId) => {
  const res = await api.delete(`/alerts/${alertId}`);
  return res.data;
};

export const testTelegram = async () => {
  const res = await api.post('/alerts/test', {});
  return res.data;
};

export const connectTelegram = async (uid) => {
  const res = await api.post('/alerts/connect', { uid });
  return res.data;
};

export const disconnectTelegram = async (uid, chatId) => {
  const res = await api.post('/alerts/disconnect', { uid, chat_id: chatId });
  return res.data;
};

export const getTelegramStatus = async (uid) => {
  try {
    const res = await api.get(`/users/${uid}`);
    return res.data;
  } catch (err) {
    return null;
  }
};

export default api;