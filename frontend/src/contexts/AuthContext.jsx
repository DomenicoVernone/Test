/* eslint-disable react-refresh/only-export-components */
/**
 * Contesto Globale di Autenticazione.
 * Gestisce lo stato della sessione attiva (Token JWT) nella memoria di React,
 * sincronizzandolo con il localStorage. 
 * Implementa il pattern 'useAuth' per incapsulare il contesto.
 */
import React, { createContext, useState, useEffect, useContext } from 'react';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
    const [token, setToken] = useState(localStorage.getItem('access_token') || null);

    const login = (jwt) => {
        setToken(jwt);
        localStorage.setItem('access_token', jwt);
    };

    const logout = () => {
        setToken(null);
        localStorage.removeItem('access_token');
        window.location.href = '/login';
    };

    // Sincronizzazione Multi-Tab
    useEffect(() => {
        const handleStorageChange = (e) => {
            if (e.key === 'access_token') {
                setToken(e.newValue);
                if (!e.newValue) {
                    window.location.href = '/login';
                }
            }
        };
        window.addEventListener('storage', handleStorageChange);
        return () => window.removeEventListener('storage', handleStorageChange);
    }, []);

    return (
        <AuthContext.Provider value={{ token, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
};

// --- CLEAN ARCHITECTURE: CUSTOM HOOK ---
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth deve essere utilizzato all'interno di un AuthProvider");
    }
    return context;
};