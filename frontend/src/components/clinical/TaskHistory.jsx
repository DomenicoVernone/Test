/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';

export default function TaskHistory() {
    const { token } = useContext(AuthContext);
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchTasks = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/analyze/', {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            if (response.ok) {
                const data = await response.json();
                setTasks(data);
            }
        } catch (error) {
            console.error("Errore nel recupero dello storico:", error);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchTasks();
    }, []); // Esegue solo al montaggio

    return (
        <div className="h-full flex flex-col p-4 bg-white">
            <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-slate-800 text-sm tracking-wide">STORICO PAZIENTI</h3>
                <button onClick={fetchTasks} className="text-xs text-clinical-primary hover:underline">
                    Aggiorna
                </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2">
                {isLoading ? (
                    <div className="text-center text-xs text-slate-400 py-4">Caricamento...</div>
                ) : tasks.length === 0 ? (
                    <div className="text-center text-xs text-slate-400 py-4 italic">
                        Nessuna analisi precedente trovata.
                    </div>
                ) : (
                    <div className="flex flex-col gap-3">
                        {tasks.map(task => (
                            <div key={task.id} className="p-3 border border-slate-100 rounded-lg shadow-sm bg-slate-50 flex flex-col gap-1">
                                <div className="flex justify-between items-center">
                                    <span className="text-xs font-semibold text-slate-700 truncate max-w-37.5" title={task.filename}>
                                        {task.filename}
                                    </span>
                                    <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase ${task.status === 'PENDING' ? 'bg-amber-100 text-amber-700' :
                                            task.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-700' :
                                                'bg-slate-200 text-slate-600'
                                        }`}>
                                        {task.status}
                                    </span>
                                </div>
                                <div className="text-[10px] text-slate-400">
                                    {new Date(task.created_at).toLocaleDateString()} - {new Date(task.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}