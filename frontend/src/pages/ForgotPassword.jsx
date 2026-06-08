import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Mail } from 'lucide-react';
import api from '../services/api';

export default function ForgotPassword({ theme }) {
    const [email, setEmail] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [submitted, setSubmitted] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        try {
            await api.post('/forgot-password', { email: email.trim() });
        } catch (_) {
            // Always show success to prevent email enumeration
        } finally {
            setIsLoading(false);
            setSubmitted(true);
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

    return (
        <div className={`min-h-screen flex items-center justify-center p-4 transition-colors duration-300 ${pageBgClass}`}>
            <div className={`w-full max-w-md p-8 rounded-2xl border transition-colors ${cardClass}`}>

                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center mx-auto mb-4">
                        <Activity className="w-8 h-8 text-clinical-primary dark:text-blue-400" />
                    </div>
                    <h1 className="text-2xl font-bold tracking-tight">Password Dimenticata</h1>
                    <p className={`text-sm mt-2 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                        Inserisci l'email associata al tuo account
                    </p>
                </div>

                {submitted ? (
                    <div className="text-center space-y-4 animate-in fade-in">
                        <div className="p-4 bg-green-50 dark:bg-green-900/30 border border-green-200 dark:border-green-800 rounded-xl">
                            <p className={`text-sm font-medium ${isDark ? 'text-green-300' : 'text-green-700'}`}>
                                Se l'email è registrata riceverai le istruzioni entro pochi minuti.
                                Controlla anche la cartella spam.
                            </p>
                        </div>
                        <Link to="/login" className={`block text-sm font-semibold ${linkClass}`}>
                            Torna al login
                        </Link>
                    </div>
                ) : (
                    <>
                        <form onSubmit={handleSubmit} className="space-y-5">
                            <div className="space-y-1">
                                <label className={`text-sm font-bold ${isDark ? 'text-slate-300' : 'text-slate-700'}`}>
                                    Email
                                </label>
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="w-5 h-5 text-slate-400" />
                                    </div>
                                    <input
                                        type="email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        required
                                        className={`w-full pl-10 pr-4 py-3 rounded-xl border focus:outline-none focus:ring-2 transition-colors ${inputClass}`}
                                        placeholder="dr.rossi@ospedale.it"
                                    />
                                </div>
                            </div>

                            <button
                                type="submit"
                                disabled={isLoading || !email.trim()}
                                className={`w-full py-3 px-4 rounded-xl font-bold tracking-wide transition-all flex justify-center items-center gap-2
                                    ${isLoading || !email.trim()
                                        ? 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200 shadow-none dark:bg-slate-800/50 dark:text-slate-500 dark:border-slate-700'
                                        : 'bg-clinical-primary text-white hover:bg-blue-600 active:scale-[0.98] shadow-md'
                                    }`}
                            >
                                {isLoading ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        Invio in corso...
                                    </>
                                ) : (
                                    'Invia Istruzioni'
                                )}
                            </button>
                        </form>

                        <p className={`text-center text-sm mt-6 ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                            <Link to="/login" className={`font-semibold ${linkClass}`}>
                                Torna al login
                            </Link>
                        </p>
                    </>
                )}
            </div>
        </div>
    );
}
