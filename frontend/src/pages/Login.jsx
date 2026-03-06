/*
  L'interfaccia utente che cattura le credenziali del medico e chiama l'endpoint /login del backend.
*/
import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { Brain } from 'lucide-react';

export default function Login() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    
    const { login } = useContext(AuthContext);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        // Chiama la funzione di login
        const result = await login(username, password);
        
        if (result.success) {
            navigate('/dashboard', { replace: true });
        } else {
            setError(result.error);
            setIsLoading(false);
        }
    };

    return (
        <div className="h-screen w-full bg-clinical-bg flex items-center justify-center font-sans">
            <div className="bg-clinical-surface p-8 rounded-2xl border border-clinical-border shadow-clinical-sm w-full max-w-md">
                <div className="flex flex-col items-center mb-8">
                    <div className="bg-blue-50 p-3 rounded-full mb-4">
                        <Brain className="w-8 h-8 text-clinical-primary" />
                    </div>
                    <h1 className="text-2xl font-bold text-slate-900">Clinical Twin</h1>
                    <p className="text-clinical-secondary text-sm mt-1">Accesso Riservato al Personale Medico</p>
                </div>

                {error && (
                    <div className="bg-red-50 text-red-600 p-3 rounded-xl text-sm mb-6 border border-red-100 text-center font-medium">
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="flex flex-col gap-5">
                    <div>
                        <label className="block text-xs font-bold text-slate-700 uppercase mb-2">Username / Email</label>
                        <input 
                            type="text" 
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className="w-full p-3 rounded-xl border border-slate-200 focus:border-clinical-primary focus:ring-2 focus:ring-blue-100 outline-none transition-all"
                            placeholder="dr.rossi@hospital.com"
                            required 
                        />
                    </div>
                    
                    <div>
                        <label className="block text-xs font-bold text-slate-700 uppercase mb-2">Password</label>
                        <input 
                            type="password" 
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full p-3 rounded-xl border border-slate-200 focus:border-clinical-primary focus:ring-2 focus:ring-blue-100 outline-none transition-all"
                            placeholder="••••••••"
                            required 
                        />
                    </div>

                    <button 
                        type="submit" 
                        disabled={isLoading}
                        className="mt-4 w-full py-4 bg-clinical-primary hover:opacity-95 disabled:bg-slate-300 rounded-xl font-bold text-white transition-all shadow-lg shadow-blue-200 active:scale-95 flex justify-center items-center"
                    >
                        {isLoading ? "Autenticazione in corso..." : "ACCEDI AL SISTEMA"}
                    </button>
                </form>
            </div>
        </div>
    );
}