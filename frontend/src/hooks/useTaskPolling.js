/**
 * Custom Hook per la gestione dello Storico Task e del Polling Asincrono.
 * Interroga il backend tramite l'istanza Axios centralizzata e aggiorna lo stato
 * in real-time se ci sono task in elaborazione ('PENDING', 'PROCESSING', 'ANALYZING_R').
 *
 * @param {number} refreshTrigger - Contatore per forzare un refresh manuale dei task.
 * @param {Function} onTaskCompleted - Callback invocata quando un task passa a 'COMPLETED'.
 * @returns {Object} { tasks, isLoading, fetchTasks } - Stato e metodi per il componente visivo.
 */
import { useState, useEffect, useCallback } from 'react';
import api from '../services/api';

export function useTaskPolling(refreshTrigger, onTaskCompleted) {
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    // useCallback previene re-rendering infiniti
    const fetchTasks = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await api.get('/analyze/');
            setTasks(response.data);
        } catch (error) {
            console.error("🚨 [Hook] Errore nel recupero dello storico:", error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    // Trigger iniziale e trigger manuale dalla Dashboard
    useEffect(() => {
        fetchTasks();
    }, [fetchTasks, refreshTrigger]);

    // Logica del Polling
    useEffect(() => {
        let intervalId;
        const activeTasks = tasks.filter(t => ['PENDING', 'PROCESSING', 'ANALYZING_R'].includes(t.status));

        if (activeTasks.length > 0) {
            intervalId = setInterval(async () => {
                const updatedTasks = [...tasks];
                let hasChanges = false;

                for (let task of activeTasks) {
                    try {
                        const res = await api.get(`/analyze/status/${task.id}`);
                        const data = res.data;
                        
                        if (data.status !== task.status) {
                            const index = updatedTasks.findIndex(t => t.id === task.id);
                            if (index !== -1) {
                                updatedTasks[index] = { ...updatedTasks[index], status: data.status };
                                hasChanges = true;
                                
                                if (data.status === 'COMPLETED' && onTaskCompleted) {
                                    onTaskCompleted(data, updatedTasks[index]); 
                                }
                            }
                        }
                    } catch (err) {
                        console.error(`⚠️ [Hook] Errore polling task ${task.id}:`, err);
                    }
                }

                if (hasChanges) setTasks(updatedTasks);
            }, 3000);
        }

        return () => { if (intervalId) clearInterval(intervalId); };
    }, [tasks, onTaskCompleted]);

    return { tasks, isLoading, fetchTasks };
}