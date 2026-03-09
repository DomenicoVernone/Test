/**
 * Entry Point e Router Principale dell'applicazione React.
 * Configura il routing lato client e avvolge l'app nei Provider di stato globali.
 * Applica la separazione rigorosa tra rotte pubbliche e rotte private.
 */
import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';

import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import ProtectedRoute from './routes/ProtectedRoute';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Rotta Pubblica: Autenticazione */}
          <Route path="/login" element={<Login />} />
          
          {/* Rotta Privata: Area Medica (Protetta dal Guardiano JWT) */}
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Fallback Catch-All: Reindirizza al nodo centrale */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}