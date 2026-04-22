import axios from 'axios';

const AUTH_URL = import.meta.env.VITE_AUTH_URL || 'http://localhost:8000';
const ORCHESTRATOR_URL = import.meta.env.VITE_ORCHESTRATOR_URL || 'http://localhost:8001';
const LLM_URL = import.meta.env.VITE_LLM_URL || 'http://localhost:8002';

const createApiInstance = (baseURL) => {
    const instance = axios.create({
        baseURL,
        /*headers: { 'Content-Type': 'application/json' },*/
    });

    instance.interceptors.request.use(
        (config) => {
            const token = localStorage.getItem('access_token');
            if (token) config.headers.Authorization = `Bearer ${token}`;
            return config;
        },
        (error) => Promise.reject(error)
    );

    instance.interceptors.response.use(
        (response) => response,
        (error) => {
            if (error.response && error.response.status === 401) {
                console.warn("🚨 Token JWT scaduto. Logout forzato.");
                localStorage.removeItem('access_token');
                window.location.href = '/login';
            }
            return Promise.reject(error);
        }
    );

    return instance;
};

export const authApi = createApiInstance(AUTH_URL);
export const orchestratorApi = createApiInstance(ORCHESTRATOR_URL);
export const llmApi = createApiInstance(LLM_URL);

export default authApi;