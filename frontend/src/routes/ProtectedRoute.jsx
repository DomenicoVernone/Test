/**
 * Guardiano di Rotta (Higher-Order Component).
 * Intercetta la navigazione e verifica la presenza del token JWT.
 * Se l'utente non è autenticato, lo reindirizza forzatamente alla pagina di Login,
 * proteggendo i componenti figli (come la Dashboard).
 *
 * @param {Object} props
 * @param {React.ReactNode} props.children - I componenti da renderizzare se l'utente è autorizzato.
 */
import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';

export default function ProtectedRoute({ children }) {
  const location = useLocation();
  const token = localStorage.getItem('access_token');

  if (!token) {
    console.warn("[Security] Accesso negato: Token JWT mancante. Reindirizzamento al Login.");
    // Usiamo l'attributo 'state' per ricordare da dove veniva l'utente (utile per redirect futuri)
    // Usiamo 'replace' per impedire che l'utente torni indietro alla route protetta premendo "Indietro" nel browser
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Se il token è presente, renderizza i componenti figli (es. <Dashboard />)
  return children;
}