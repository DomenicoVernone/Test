import { useState, useEffect, useCallback } from 'react';
import { orchestratorApi } from '../services/api';

export function useTaskPolling(refreshTrigger, onTaskCompleted) {
    const [tasks, setTasks] = useState([]);
    const [isLoading, setIsLoading] = useState(true);

    const fetchTasks = useCallback(async () => {
        setIsLoading(true);
        try {
            const response = await orchestratorApi.get('/analyze/');
            setTasks(response.data);
        } catch (error) {
            console.error("[useTaskPolling] Errore nel recupero dello storico:", error);
        } finally {
            setIsLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchTasks();
    }, [fetchTasks, refreshTrigger]);

    useEffect(() => {
        let intervalId;
        const activeTasks = tasks.filter(t => ['PENDING', 'PROCESSING', 'ANALYZING_R'].includes(t.status));

        if (activeTasks.length > 0) {
            intervalId = setInterval(async () => {
                const updatedTasks = [...tasks];
                let hasChanges = false;

                for (let task of activeTasks) {
                    try {
                        const res = await orchestratorApi.get(`/analyze/status/${task.id}`);
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
                        console.error(`[useTaskPolling] Errore polling task ${task.id}:`, err);
                    }
                }

                if (hasChanges) setTasks(updatedTasks);
            }, 3000);
        }

        return () => { if (intervalId) clearInterval(intervalId); };
    }, [tasks, onTaskCompleted]);

    return { tasks, isLoading, fetchTasks };
}