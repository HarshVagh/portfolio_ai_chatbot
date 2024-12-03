import axios from 'axios';

const apiUrl = `${window.location.protocol}//${window.location.hostname}`;

console.log("API URL:", apiUrl);

const AxiosInstance = axios.create({
  baseURL: apiUrl,
});

AxiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default AxiosInstance;