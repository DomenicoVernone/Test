import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';

export default function ProtectedRoute({ children }) {
    const { isAuthenticated } = useContext(AuthContext);

    if (!isAuthenticated) {
        // Se non c'è il token, redirige forzatamente al login
        return <Navigate to="/login" replace />;
    }

    // Se l'utente ha il JWT, renderizza il contenuto protetto
    return children;
}