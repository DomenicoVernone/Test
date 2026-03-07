/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect, useContext } from 'react';
import { AuthContext } from '../../contexts/AuthContext';

export default function TaskHistory({ onTaskCompleted, onTaskClick }) {
    const { token } = useContext(AuthContext);
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchTasks = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('http://localhost:8000/analyze/', {
                method: 'GET',
                headers: { 'Authorization': `Bearer ${token}` }
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
        let intervalId;
        const activeTasks = tasks.filter(t => ['PENDING', 'PROCESSING', 'NEXTFLOW_COMPLETED'].includes(t.status));

        if (activeTasks.length > 0) {
            intervalId = setInterval(async () => {
                const updatedTasks = [...tasks];
                let hasChanges = false;

                for (let task of activeTasks) {
                    try {
                        const res = await fetch(`http://localhost:8000/analyze/status/${task.id}`, {
                            headers: { 'Authorization': `Bearer ${token}` }
                        });
                        
                        if (res.ok) {
                            const data = await res.json();
                            if (data.status !== task.status) {
                                const index = updatedTasks.findIndex(t => t.id === task.id);
                                if (index !== -1) {
                                    updatedTasks[index] = { ...updatedTasks[index], status: data.status };
                                    hasChanges = true;
                                    if (data.status === 'COMPLETED' && onTaskCompleted) {
                                        onTaskCompleted(data, updatedTasks[index]); // Passiamo anche i meta-dati del task
                                    }
                                }
                            }
                        }
                    } catch (err) {
                        console.error(`Errore nel polling del task ${task.id}:`, err);
                    }
                }

                if (hasChanges) setTasks(updatedTasks);
            }, 3000);
        }

        return () => { if (intervalId) clearInterval(intervalId); };
    }, [tasks, token, onTaskCompleted]);

    useEffect(() => { fetchTasks(); }, []);

    // GESTIONE DEL CLICK SULLA CARD
    const handleCardClick = async (task) => {
        if (task.status !== 'COMPLETED') return; // I task non completati non sono navigabili
        
        try {
            // 1. Recupera i dati UMAP (JSON) dal backend
            const res = await fetch(`http://localhost:8000/analyze/status/${task.id}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (res.ok) {
                const data = await res.json();
                if (onTaskClick) {
                    // Passiamo al padre: il JSON (data), l'URL del NIfTI, e il nome del modello (es. HC_vs_bvFTD)
                    onTaskClick({
                        umapData: data.plot_data,
                        prediction: data.diagnosi_predetta,
                        niftiUrl: `http://localhost:8000/analyze/nifti/${task.id}`,
                        modelName: task.model_name 
                    });
                }
            }
        } catch (err) {
            console.error("Errore nel caricamento del task storico:", err);
        }
    };

    return (
        <div className="h-full flex flex-col p-4 bg-white">
            <div className="flex justify-between items-center mb-4">
                <h3 className="font-bold text-slate-800 text-sm tracking-wide">STORICO PAZIENTI</h3>
                <button onClick={fetchTasks} className="text-xs text-clinical-primary hover:underline">Aggiorna</button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2">
                {isLoading ? (
                    <div className="text-center text-xs text-slate-400 py-4">Caricamento...</div>
                ) : tasks.length === 0 ? (
                    <div className="text-center text-xs text-slate-400 py-4 italic">Nessuna analisi precedente.</div>
                ) : (
                    <div className="flex flex-col gap-3">
                        {tasks.map(task => (
                            <div 
                                key={task.id} 
                                onClick={() => handleCardClick(task)}
                                className={`p-3 border rounded-lg shadow-sm flex flex-col gap-1 transition-all
                                    ${task.status === 'COMPLETED' ? 'bg-slate-50 border-slate-200 cursor-pointer hover:border-clinical-primary hover:shadow-md' : 'bg-slate-50/50 border-slate-100 opacity-70 cursor-not-allowed'}`}
                            >
                                <div className="flex justify-between items-center">
                                    <span className="text-xs font-semibold text-slate-700 truncate max-w-37.5" title={task.filename}>
                                        {task.filename}
                                    </span>
                                    <span className={`text-[9px] px-2 py-0.5 rounded-full font-bold uppercase 
                                        ${['PENDING', 'PROCESSING', 'NEXTFLOW_COMPLETED'].includes(task.status) ? 'bg-amber-100 text-amber-700' : task.status === 'COMPLETED' ? 'bg-emerald-100 text-emerald-700' : 'bg-red-100 text-red-700'}`}>
                                        {['PENDING', 'PROCESSING', 'NEXTFLOW_COMPLETED'].includes(task.status) ? 'IN ELABORAZIONE' : task.status === 'COMPLETED' ? 'COMPLETATO' : 'ERRORE'}
                                    </span>
                                </div>
                                <div className="text-[10px] text-slate-400 flex justify-between">
                                    <span>{new Date(task.created_at).toLocaleDateString()}</span>
                                    {task.model_name && <span className="uppercase font-semibold tracking-wider">{task.model_name.replace('HC_vs_', '')}</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}