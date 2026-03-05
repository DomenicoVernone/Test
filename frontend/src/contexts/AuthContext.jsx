import React, { createContext, useState } from 'react';
import { authService } from '../services/authService';
// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    // Inizializziamo lo stato leggendo dal localStorage (utile se si ricarica la pagina)
    const [token, setToken] = useState(localStorage.getItem('access_token') || null);
    const [isAuthenticated, setIsAuthenticated] = useState(!!token);

    const login = async (username, password) => {
        try {
            const data = await authService.login(username, password);
            const jwt = data.access_token;
            
            // Salviamo in memoria e nel localStorage
            setToken(jwt);
            setIsAuthenticated(true);
            localStorage.setItem('access_token', jwt);
            
            return { success: true };
        } catch (error) {
            console.error("Errore di login:", error);
            return { 
                success: false, 
                error: error.response?.data?.detail || "Errore di connessione al server" 
            };
        }
    };

    const logout = () => {
        setToken(null);
        setIsAuthenticated(false);
        localStorage.removeItem('access_token');
    };

    return (
        <AuthContext.Provider value={{ isAuthenticated, token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};