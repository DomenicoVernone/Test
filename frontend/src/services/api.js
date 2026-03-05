import axios from 'axios';

// Creiamo un'istanza base configurata per il nostro futuro backend FastAPI
const api = axios.create({
    baseURL: 'http://localhost:8000',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor: prima di far partire QUALSIASI richiesta, esegue questo blocco
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;