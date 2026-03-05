import api from './api';

export const authService = {
    login: async (username, password) => {
        // FastAPI (legacy Pracella) si aspetta i dati del login in questo formato
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await api.post('/login', formData, {
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        });
        return response.data;
    },

    signup: async (userData) => {
        const response = await api.post('/signup', userData);
        return response.data;
    }
};