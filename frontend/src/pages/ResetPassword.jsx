import React, { useState } from 'react';
import { useNavigate, useSearchParams, Link } from 'react-router-dom';
import { Activity, Lock, CheckCircle2, XCircle, ShieldAlert } from 'lucide-react';
import api from '../services/api';

const passwordChecks = (pwd) => [
    { label: 'Minimo 8 caratteri', ok: pwd.length >= 8 },
    { label: 'Almeno una maiuscola', ok: /[A-Z]/.test(pwd) },
    { label: 'Almeno un numero', ok: /[0-9]/.test(pwd) },
];

export default function ResetPassword({ theme }) {
    const [searchParams] = useSearchParams();
    const token = searchParams.get('token') || '';

    const [password, setPassword] = useState('');
    const [confirm, setConfirm] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState('');
    const [tokenInvalid, setTokenInvalid] = useState(!token);
    const navigate = useNavigate();

    const checks = passwordChecks(password);
    const allOk = checks.every((c) => c.ok);
    const isFormValid = password && allOk && password === confirm;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setError('');
        try {
            await api.post('/reset-password', { token, new_password: password });
            navigate('/login', { state: { message: 'Password aggiornata. Accedi con le nuove credenziali.' } });
        } catch (err) {
            if (err.response?.status === 400) {
                setTokenInvalid(true);
            } else {
                setError('Impossibile connettersi al server. Riprova più tardi.');
            }
        } finally {
            setIsLoading(false);
        }
    };

    const isDark = theme === 'dark';
    const pageBgClass = isDark ? 'bg-slate-900' : 'bg-slate-50';
    const cardClass = isDark
        ? 'bg-slate-800 border-slate-700 text-slate-100 shadow-2xl'
        : 'bg-white border-slate-200 text-slate-900 shadow-xl';
    const inputClass = isDark
        ? 'bg-slate-900 border-slate-600 text-white focus:ring-blue-500'
        : 'bg-slate-50 border-slate-300 text-slate-900 focus:ring-clinical-primary';
    const linkClass = isDark
        ? 'text-blue-400 hover:text-blue-300'
        : 'text-clinical-primary hover:text-blue-700';

    if (tokenInvalid) {
        return (
            <div className={`min-h-screen flex items-center justify-center p-4 ${pageBgClass}`}>
                <div className={`w-full max-w-md p-8 rounded-2xl border text-center space-y-4 ${cardClass}`}>
                    <ShieldAlert className="w-12 h-12 text-red-400 mx-auto" />
                    <h2 className="text-xl font-bold">Link non valido o scaduto</h2>
                    <p className={`text-sm ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Il link per il reset della password è scaduto o è già stato usato.
                    </p>
                    <Link to="/forgot-password" className={`block text-sm font-semibold ${linkClass}`}>
                        Richiedi un nuovo link
                    </Link>
                </div>
            </div>
        );
    }

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Nuova Password</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Scegli una password sicura per il tuo account
                    </p>
                </div>

                {error && (
                    <div className="mb-6 p-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-xl flex items-center gap-3 text-red-600 dark:text-red-400">
                        <ShieldAlert className="w-5 h-5 shrink-0" />
                        <span className="text-sm font-semibold">{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Nuova Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="w-5 h-5 text-slate-400" />
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
                        {password && (
                            <ul className="pt-2 space-y-1">
                                {checks.map((c) => (
                                    <li key={c.label} className="flex items-center gap-2 text-xs" style={{ transition: 'color 0.2s' }}>
                                        {c.ok
                                            ? <CheckCircle2 className="w-4 h-4 text-green-500 shrink-0" />
                                            : <XCircle className="w-4 h-4 text-red-400 shrink-0" />}
                                        <span className={c.ok ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}>
                                            {c.label}
                                        </span>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>

                    <div className="space-y-1">
                        <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                            Conferma Password
                        </label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="w-5 h-5 text-slate-400" />
                            </div>
                            <input
                                type="password"
                                value={confirm}
                                onChange={(e) => setConfirm(e.target.value)}
                                required
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass} ${confirm && password !== confirm ? 'border-red-400 focus:ring-red-400' : ''}`}
                                placeholder="••••••••"
                            />
                        </div>
                        {confirm && password !== confirm && (
                            <p className="text-xs text-red-500 font-medium pt-1 animate-in fade-in">Le password non coincidono</p>
                        )}
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading || !isFormValid}
                        className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                            ${isLoading || !isFormValid
                                ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                            }`}
                    >
                        {isLoading ? (
                            <>
                                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                Aggiornamento...
                            </>
                        ) : (
                            'Aggiorna Accesso'
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
