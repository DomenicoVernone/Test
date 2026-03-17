/**
 * Pagina di Autenticazione (Login).
 * Raccoglie le credenziali del medico e dialoga con l'endpoint `/login` del backend
 * utilizzando il formato 'application/x-www-form-urlencoded' richiesto da FastAPI.
 *
 * @param {Object} props
 * @param {string} props.theme - Tema grafico attuale ('light' o 'dark').
 */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Lock, User, ShieldAlert } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

import api from '../services/api';

export default function Login({ theme }) {

    const { login } = useAuth();

    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');

    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        // FastAPI aspetta un form OAuth2 (x-www-form-urlencoded), NON un JSON!
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await api.post('/login', formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
            });

            // Salvataggio sicuro tramite il Context (aggiorna stato e localStorage)
            login(response.data.access_token);

            // Reindirizzamento alla Dashboard
            navigate('/dashboard');
        } catch (err) {
            console.error("🚨 Errore di Login:", err);
            // Cattura il messaggio di errore dal backend (401 Unauthorized) o mostra un fallback
            const errorMsg = err.response?.data?.detail || "Impossibile connettersi al server. Riprova più tardi.";
            setError(errorMsg);
        } finally {
            setIsLoading(false);
        }
    };

    // --- CLEAN CODE per le Classi Tailwind (Dark Mode) ---
    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl' : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500' : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const iconClass = isDark ? 'text-slate-400' : 'text-slate-400';

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Clinical Twin</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Accesso riservato al personale medico autorizzato
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400 animate-in fade-in slide-in-from-top-2">
                        <ShieldAlert className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">{error}</span>
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-5">
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Identificativo Medico</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <User className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="Inserisci il tuo username..."
                            />
                        </div>
                    </div>

                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>Password</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className={`w-5 h-5 ${iconClass}`} />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                placeholder="••••••••"
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || !username || !password}
                        className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2 
              ${isLoading || !username || !password
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'}`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                Autenticazione...
                            </>
                        ) : (
                            'Accedi al Sistema'
                        )}
                    </button>
                </form>

                <p className={`text-center text-xs mt-8 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    Progetto di Ricerca Accademica • Uso Esclusivo di Ricerca (RUO)                </p>
            </div>
        </div>
    );
}