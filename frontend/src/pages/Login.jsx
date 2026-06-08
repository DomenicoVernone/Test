import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { Activity, Lock, User, ShieldAlert, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';

const FAIL_KEY = 'login_fails';
const LOCK_KEY = 'login_locked_until';
const MAX_FAILS = 3;
const LOCK_SECONDS = 60;

export default function Login({ theme }) {
    const { login } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [lockSecondsLeft, setLockSecondsLeft] = useState(0);
    const timerRef = useRef(null);
    const navigate = useNavigate();
    const location = useLocation();
    const successMessage = location.state?.message || '';

    useEffect(() => {
        const tick = () => {
            const until = parseInt(localStorage.getItem(LOCK_KEY) || '0');
            const left = Math.ceil((until - Date.now()) / 1000);
            if (left > 0) {
                setLockSecondsLeft(left);
            } else {
                setLockSecondsLeft(0);
                clearInterval(timerRef.current);
            }
        };
        tick();
        timerRef.current = setInterval(tick, 1000);
        return () => clearInterval(timerRef.current);
    }, []);

    const recordFail = () => {
        const fails = parseInt(localStorage.getItem(FAIL_KEY) || '0') + 1;
        localStorage.setItem(FAIL_KEY, String(fails));
        if (fails >= MAX_FAILS) {
            const until = Date.now() + LOCK_SECONDS * 1000;
            localStorage.setItem(LOCK_KEY, String(until));
            localStorage.setItem(FAIL_KEY, '0');
        }
    };

    const clearFails = () => {
        localStorage.removeItem(FAIL_KEY);
        localStorage.removeItem(LOCK_KEY);
    };

    const handleLogin = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');

        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await api.post('/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            });
            clearFails();
            login(response.data.access_token);
            navigate('/dashboard');
        } catch (err) {
            recordFail();
            setError('Credenziali non valide');
        } finally {
            setIsLoading(false);
        }
    };

    const isLocked = lockSecondsLeft > 0;
    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark
        ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl'
        : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark
        ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500'
        : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const iconClass = 'text-slate-400';
    const linkClass = isDark ? 'text-blue-400 hover:text-blue-300' : 'text-clinical-primary hover:text-blue-700';

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

                {successMessage && (
                    <div className="mb-6 p-3 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl flex items-center gap-3 text-green-600 dark:text-green-400 animate-in fade-in slide-in-from-top-2">
                        <CheckCircle2 className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">{successMessage}</span>
                    </div>
                )}

                {(error || isLocked) && (
                    <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400 animate-in fade-in slide-in-from-top-2">
                        <ShieldAlert className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">
                            {isLocked ? `Riprova tra ${lockSecondsLeft}s...` : error}
                        </span>
                    </div>
                )}

                <form onSubmit={handleLogin} className="space-y-5">
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Identificativo Medico
                        </label>
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
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Password
                        </label>
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
                        <div className="flex justify-end pt-1">
                            <Link to="/forgot-password" className={`text-xs font-medium ${linkClass}`}>
                                Password dimenticata?
                            </Link>
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || isLocked || !username || !password}
                        className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                            ${isLoading || isLocked || !username || !password
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                            }`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Autenticazione...
                            </>
                        ) : (
                            'Accedi al Sistema'
                        )}
                    </button>
                </form>

                <p className={`text-center text-sm mt-6 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                    Prima volta?{' '}
                    <Link to="/register" className={`font-semibold ${linkClass}`}>
                        Richiedi accesso
                    </Link>
                </p>

                <p className={`text-center text-xs mt-6 ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
                    Progetto di Ricerca Accademica • Uso Esclusivo di Ricerca (RUO)
                </p>
            </div>
        </div>
    );
}
