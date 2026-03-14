/**
 * Componente Presentazionale e di Gestione Stato Locale: Storico Task.
 * Renderizza la lista delle analisi (NIfTI) e gestisce il feedback visivo in tempo reale.
 * Delega la logica di rete (polling) all'hook custom 'useTaskPolling'.
 *
 * @param {Object} props
 * @param {Function} props.onTaskCompleted - Callback invocata quando un task passa allo stato 'COMPLETED'.
 * @param {Function} props.onTaskClick - Callback invocata al click su una card completata per visualizzare UMAP e 3D.
 * @param {string} props.theme - Tema grafico attuale dell'interfaccia ('light' o 'dark').
 * @param {number} props.refreshHistoryTrigger - Contatore numerico per forzare il refresh manuale dello storico.
 */
import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import { useTaskPolling } from '../../hooks/useTaskPolling';

// --- HELPER DI FORMATTAZIONE DATE (FIX FUSO ORARIO UTC/CET) ---
/**
 * Forza l'interpretazione della data in formato UTC.
 * Previene discrepanze di fuso orario tra il server (FastAPI) e il client (Browser).
 * * @param {string} dateStr - Stringa ISO della data proveniente dal backend.
 * @returns {Date} Oggetto Date nativo in formato UTC.
 */
const parseDateSicura = (dateStr) => {
    if (!dateStr) return new Date();
    let str = dateStr;
    if (str.includes(' ')) str = str.replace(' ', 'T'); // Converte l'output SQL in ISO standard
    if (!str.endsWith('Z')) str += 'Z'; // Forza il fuso orario UTC appendendo 'Z'
    return new Date(str);
};

// --- MICRO-COMPONENTE: TIMER IN TEMPO REALE ---
/**
 * Timer isolato per i task in elaborazione.
 * Si aggiorna autonomamente ogni secondo senza causare re-render dell'intera lista.
 * * @param {Object} props
 * @param {string} props.startTime - Timestamp di inizio del task.
 * @param {string} props.theme - Tema grafico attuale.
 */
const LiveTimer = ({ startTime, theme }) => {
    const [elapsed, setElapsed] = useState(0);

    useEffect(() => {
        if (!startTime) return;

        const startTimestamp = parseDateSicura(startTime).getTime();

        const tick = () => {
            const now = new Date().getTime();
            // Math.max evita numeri negativi dovuti a latenze di rete di pochi millisecondi
            setElapsed(Math.max(0, Math.floor((now - startTimestamp) / 1000)));
        };

        tick(); // Esecuzione immediata per evitare il delay di 1s iniziale
        const intervalId = setInterval(tick, 1000);

        return () => clearInterval(intervalId); // Cleanup al completamento o smontaggio
    }, [startTime]);

    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    const display = minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;

    return (
        <span className={`flex items-center gap-1 font-medium ${theme === 'dark' ? 'text-amber-400/80' : 'text-amber-600'}`}>
            ⏳ {display}
        </span>
    );
};

export default function TaskHistory({ onTaskCompleted, onTaskClick, theme, refreshHistoryTrigger }) {

    // Astrazione della logica di polling API
    const { tasks, isLoading, fetchTasks } = useTaskPolling(refreshHistoryTrigger, onTaskCompleted);

    // --- FUNZIONI HELPER DI FORMATTAZIONE (UI) ---

    /**
     * Pulisce il nome del file rimuovendo l'UUID generato dal backend.
     * @param {string} filename - Nome del file originale (es. '123e4567..._paziente1.nii').
     * @returns {string} Nome pulito (es. 'paziente1.nii').
     */
    const formatFilename = (filename) => {
        if (!filename) return "Sconosciuto";
        const firstUnderscoreIndex = filename.indexOf('_');
        if (firstUnderscoreIndex !== -1 && firstUnderscoreIndex === 36) {
            return filename.substring(firstUnderscoreIndex + 1);
        }
        return filename;
    };

    /**
     * Formatta il timestamp per la visualizzazione dell'Audit Trail.
     * @param {string} dateString - Data in formato ISO.
     * @returns {string} Data formattata (es. '09/03/2026 14:30').
     */
    const formatTimestamp = (dateString) => {
        if (!dateString) return "";
        const d = parseDateSicura(dateString);
        return d.toLocaleDateString('it-IT', {
            day: '2-digit', month: '2-digit', year: 'numeric',
            hour: '2-digit', minute: '2-digit'
        }).replace(',', '');
    };

    /**
     * Calcola la durata statica totale di un task completato.
     * Implementa meccanismi di fallback per latenze di aggiornamento del DB.
     * * @param {string} start - Timestamp inizio.
     * @param {string} end - Timestamp fine (updated_at).
     * @param {string} status - Stato corrente del task.
     * @returns {string|null} Durata formattata o null se non completato.
     */
    const calculateDuration = (start, end, status) => {
        if (status !== 'COMPLETED' || !start) return null;

        const startTime = parseDateSicura(start).getTime();

        // Fallback: se 'end' non è ancora stato propagato o è identico a 'start',
        // usiamo l'istante attuale come stima di completamento per evitare '0s'.
        let endTime = end ? parseDateSicura(end).getTime() : new Date().getTime();

        if (endTime <= startTime + 1000) {
            endTime = new Date().getTime();
        }

        const diffInSeconds = Math.max(1, Math.floor((endTime - startTime) / 1000));

        if (diffInSeconds < 60) return `${diffInSeconds}s`;

        const minutes = Math.floor(diffInSeconds / 60);
        const seconds = diffInSeconds % 60;
        return `${minutes}m ${seconds}s`;
    };

    // --- HANDLER EVENTI ---

    const handleCardClick = async (task) => {
        // Calcoliamo l'URL del NIfTI a prescindere dallo stato (FastAPI lo salva subito!)
        const baseURL = api.defaults.baseURL || 'http://localhost:8000';
        const niftiUrl = `${baseURL}/analyze/nifti/${task.id}/volume.nii.gz`;

        if (task.status === 'COMPLETED') {
            try {
                const res = await api.get(`/analyze/status/${task.id}`);
                const data = res.data;
                if (onTaskClick) {
                    onTaskClick({
                        taskId: task.id,
                        umapData: data.plot_data,
                        prediction: data.diagnosi_predetta,
                        niftiUrl: niftiUrl,
                        modelName: task.model_name,
                        status: task.status // Passiamo lo stato al genitore!
                    });
                }
            } catch (err) {
                console.error("Errore nel caricamento del task storico:", err);
            }
        } else {
            // MAGIA: Il task sta ancora frullando, ma passiamo lo stesso il NIfTI!
            if (onTaskClick) {
                onTaskClick({
                    taskId: task.id,
                    umapData: null,
                    prediction: null,
                    niftiUrl: niftiUrl,
                    modelName: task.model_name,
                    status: task.status // Segnaliamo che è ancora in corso
                });
            }
        }
    };

    // --- STILI E CLASSI DINAMICHE ---

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

    // --- RENDER ---
    return (
        <div className={`h-full flex flex-col p-4 transition-colors duration-300 ${theme === 'dark' ? 'bg-slate-900' : 'bg-white'}`}>
            {/* Header Sidebar */}
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

            {/* Lista Task */}
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
                        {tasks.map(task => {
                            const cleanName = formatFilename(task.filename);
                            const auditTime = formatTimestamp(task.created_at);
                            const duration = calculateDuration(task.created_at, task.updated_at, task.status);

                            return (
                                <div
                                    key={task.id}
                                    onClick={() => handleCardClick(task)}
                                    className={`p-3 border rounded-xl shadow-sm flex flex-col gap-1 transition-all duration-200 cursor-pointer ${theme === 'dark'
                                            ? 'bg-slate-800 border-slate-700 hover:border-blue-500 hover:bg-slate-750'
                                            : 'bg-slate-50 border-slate-200 hover:border-clinical-primary hover:shadow-md'
                                        }`}
                                >
                                    {/* Riga Superiore: Nome e Badge */}
                                    <div className="flex justify-between items-center">
                                        <span className={`text-sm font-bold truncate max-w-35 ${theme === 'dark' ? 'text-slate-200' : 'text-slate-700'}`} title={cleanName}>
                                            {cleanName}
                                        </span>

                                        <span className={`text-[9px] px-2 py-0.5 rounded-md font-bold uppercase tracking-wider border ${getBadgeStyle(task.status)}`}>
                                            {getBadgeText(task.status)}
                                        </span>
                                    </div>

                                    {/* Riga Inferiore: Audit Trail, Timer e Modello */}
                                    <div className={`text-[10px] flex justify-between items-center mt-1 ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>
                                        <div className="flex items-center gap-2">
                                            <span>{auditTime}</span>

                                            {/* RENDER CONDIZIONALE: Live Timer o Durata Statica */}
                                            {task.status === 'COMPLETED' && duration ? (
                                                <span className={`flex items-center gap-1 ${theme === 'dark' ? 'text-emerald-400/80' : 'text-emerald-600'}`}>
                                                    ⏱ {duration}
                                                </span>
                                            ) : ['PENDING', 'PROCESSING', 'ANALYZING_R'].includes(task.status) ? (
                                                <LiveTimer startTime={task.created_at} theme={theme} />
                                            ) : null}
                                        </div>

                                        {task.model_name && (
                                            <span className={`uppercase font-semibold tracking-wider px-1.5 rounded-full ${theme === 'dark' ? 'bg-slate-900 text-slate-400' : 'bg-white text-slate-500'}`}>
                                                {task.model_name.replace('HC_vs_', '')}
                                            </span>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}