/**
 * Componente per la visualizzazione dello Storico Task.
 * Sfrutta l'hook 'useTaskPolling' per separare la logica di rete dal rendering visivo.
 */
import React from 'react';
import api from '../../services/api'; 
import { useTaskPolling } from '../../hooks/useTaskPolling'; // <-- Importiamo la logica estratta

export default function TaskHistory({ onTaskCompleted, onTaskClick, theme, refreshHistoryTrigger }) {
    
    // Deleghiamo tutta la complessità del polling al custom hook!
    const { tasks, isLoading, fetchTasks } = useTaskPolling(refreshHistoryTrigger, onTaskCompleted);

    // --- HANDLER CLICK SU TASK COMPLETATO ---
    const handleCardClick = async (task) => {
        if (task.status !== 'COMPLETED') return; 
        
        try {
            const res = await api.get(`/analyze/status/${task.id}`);
            const data = res.data;
            
            if (onTaskClick) {
                const baseURL = api.defaults.baseURL || 'http://localhost:8000';
                
                onTaskClick({
                    umapData: data.plot_data,
                    prediction: data.diagnosi_predetta,
                    niftiUrl: `${baseURL}/analyze/nifti/${task.id}/volume.nii.gz`,
                    modelName: task.model_name 
                });
            }
        } catch (err) {
            console.error("🚨 Errore nel caricamento del task storico:", err);
        }
    };

    // --- FUNZIONI HELPER PER I BADGE ---
    const getBadgeStyle = (status) => {
        const isDark = theme === 'dark';
        if (['PENDING', 'PROCESSING', 'ANALYZING_R'].includes(status)) {
            return isDark ? 'bg-amber-900/40 text-amber-400 border-amber-800/50 animate-pulse' : 'bg-amber-100 text-amber-700 border-transparent animate-pulse';
        }
        if (status === 'COMPLETED') {
            return isDark ? 'bg-emerald-900/40 text-emerald-400 border-emerald-800/50' : 'bg-emerald-100 text-emerald-700 border-transparent';
        }
        return isDark ? 'bg-red-900/40 text-red-400 border-red-800/50' : 'bg-red-100 text-red-700 border-transparent';
    };

    const getBadgeText = (status) => {
        if (['PENDING', 'PROCESSING', 'ANALYZING_R'].includes(status)) return 'IN ELABORAZIONE';
        if (status === 'COMPLETED') return 'COMPLETATO';
        return 'ERRORE';
    };

    return (
        <div className={`h-full flex flex-col p-4 transition-colors duration-300 ${theme === 'dark' ? 'bg-slate-900' : 'bg-white'}`}>
            <div className="flex justify-between items-center mb-4">
                <h3 className={`font-bold text-sm tracking-wide ${theme === 'dark' ? 'text-white' : 'text-slate-800'}`}>
                    STORICO PAZIENTI
                </h3>
                <button 
                    onClick={fetchTasks} 
                    className={`text-xs hover:underline transition-colors ${theme === 'dark' ? 'text-blue-400 hover:text-blue-300' : 'text-clinical-primary'}`}
                >
                    Aggiorna
                </button>
            </div>

            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
                {isLoading ? (
                    <div className={`text-center text-xs py-4 ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                        Caricamento...
                    </div>
                ) : tasks.length === 0 ? (
                    <div className={`text-center text-xs py-4 italic ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
                        Nessuna analisi precedente.
                    </div>
                ) : (
                    <div className="flex flex-col gap-3">
                        {tasks.map(task => (
                            <div 
                                key={task.id} 
                                onClick={() => handleCardClick(task)}
                                className={`p-3 border rounded-xl shadow-sm flex flex-col gap-1 transition-all duration-200
                                    ${task.status === 'COMPLETED' 
                                        ? (theme === 'dark' ? 'bg-slate-800 border-slate-700 cursor-pointer hover:border-blue-500 hover:bg-slate-750' : 'bg-slate-50 border-slate-200 cursor-pointer hover:border-clinical-primary hover:shadow-md') 
                                        : (theme === 'dark' ? 'bg-slate-800/50 border-slate-800 opacity-60 cursor-not-allowed' : 'bg-slate-50/50 border-slate-100 opacity-70 cursor-not-allowed')
                                    }`}
                            >
                                <div className="flex justify-between items-center">
                                    <span className={`text-xs font-semibold truncate max-w-37.5 ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'}`} title={task.filename}>
                                        {task.filename}
                                    </span>
                                    
                                    <span className={`text-[9px] px-2 py-0.5 rounded-md font-bold uppercase tracking-wider border ${getBadgeStyle(task.status)}`}>
                                        {getBadgeText(task.status)}
                                    </span>
                                </div>
                                
                                <div className={`text-[10px] flex justify-between mt-1 ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                                    <span>{new Date(task.created_at).toLocaleDateString()}</span>
                                    {task.model_name && (
                                        <span className={`uppercase font-semibold tracking-wider px-1.5 rounded-full ${theme === 'dark' ? 'bg-slate-900 text-slate-400' : 'bg-white text-slate-500'}`}>
                                            {task.model_name.replace('HC_vs_', '')}
                                        </span>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}