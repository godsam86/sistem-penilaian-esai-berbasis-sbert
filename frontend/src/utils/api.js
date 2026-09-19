import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  timeout: 60000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let isRefreshing = false;
let pendingQueue = [];

function clearSessionAndRedirect() {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
  localStorage.removeItem('user');
  if (!window.location.pathname.endsWith('/login')) {
    window.location.href = '/login';
  }
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    const refresh = localStorage.getItem('refresh');

    // Access token (8 jam) kedaluwarsa -- coba refresh sekali sebelum logout paksa.
    if (error.response?.status === 401 && refresh && !original._retried) {
      original._retried = true;
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          pendingQueue.push({ resolve, reject, original });
        });
      }
      isRefreshing = true;
      try {
        const { data } = await axios.post('/api/auth/token/refresh/', { refresh });
        localStorage.setItem('access', data.access);
        pendingQueue.forEach(({ resolve, original: o }) => {
          o.headers.Authorization = `Bearer ${data.access}`;
          resolve(api(o));
        });
        pendingQueue = [];
        original.headers.Authorization = `Bearer ${data.access}`;
        return api(original);
      } catch (refreshError) {
        pendingQueue.forEach(({ reject }) => reject(refreshError));
        pendingQueue = [];
        clearSessionAndRedirect();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    if (error.response?.status === 401) {
      clearSessionAndRedirect();
    }
    return Promise.reject(error);
  }
);

export default api;
