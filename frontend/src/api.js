import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor to attach X-User-ID to all backend requests
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId');
  if (userId) {
    config.headers['X-User-ID'] = userId;
  }
  return config;
});

export const conversationApi = {
  list: async () => {
    const res = await api.get('/conversation');
    return res.data;
  },
  create: async (title = 'New Research Chat') => {
    const res = await api.post('/conversation', { title });
    return res.data;
  },
  getMessages: async (id) => {
    const res = await api.get(`/conversation/${id}/messages`);
    return res.data;
  },
  chat: async (id, query) => {
    const res = await api.post('/conversation/chat', { conversation_id: id, query });
    return res.data; // { answer, citations }
  },
  delete: async (id) => {
    const res = await api.delete(`/conversation/${id}`);
    return res.data;
  },
  updateTitle: async (id, title) => {
    const res = await api.put(`/conversation/${id}/title`, { title });
    return res.data;
  }
};

const corpusApiInstance = axios.create({
  baseURL: 'http://localhost:8001',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const corpusApi = {
  getCollectionInfo: async () => {
    const res = await corpusApiInstance.get('/collection/info');
    return res.data;
  },
  getPapers: async (limit = 50, offset = 0) => {
    const res = await corpusApiInstance.get(`/collection/papers?limit=${limit}&offset=${offset}`);
    return res.data;
  },
  startIngestion: async (queries, top_k = 5) => {
    const res = await corpusApiInstance.post('/ingest', { queries, top_k });
    return res.data;
  },
  getJobs: async () => {
    const res = await corpusApiInstance.get('/ingest/jobs');
    return res.data;
  }
};

export const paperRequestApi = {
  create: async (query) => {
    const res = await api.post('/paper-requests', { query });
    return res.data;
  },
  list: async () => {
    const res = await api.get('/paper-requests');
    return res.data;
  }
};

export default api;
