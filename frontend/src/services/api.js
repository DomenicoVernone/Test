/**
 * Servizio API Client centralizzato.
 * Configura Axios per comunicare con il backend FastAPI, iniettando automaticamente
 * il token JWT e gestendo globalmente le risposte di errore (es. token scaduto).
 */
import axios from 'axios';

// Utilizza la variabile d'ambiente di Vite, con fallback a localhost per sicurezza
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// --- REQUEST INTERCEPTOR ---
// Prima di inviare QUALSIASI richiesta, inietta il token JWT se presente
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// --- RESPONSE INTERCEPTOR ---
// Intercetta le risposte del backend prima che arrivino ai componenti React
api.interceptors.response.use(
    (response) => response,
    (error) => {
        // Se il backend risponde con 401 (Non Autorizzato/Token Scaduto)
        if (error.response && error.response.status === 401) {
            console.warn("🚨 Token JWT scaduto o non valido. Eseguo il logout forzato.");
            localStorage.removeItem('access_token');
            // Reindirizza l'utente alla pagina di login in modo brutale ma sicuro
            window.location.href = '/login'; 
        }
        return Promise.reject(error);
    }
);

export default api;