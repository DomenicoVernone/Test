// File: frontend/src/components/layout/RightSidebar.jsx
/**
 * Componente Presentazionale: Sidebar Destra.
 * Gestisce il layout a comparsa e l'alternanza dei tab tra l'Assistente LLM e lo Storico Pazienti.
 * Essendo un componente "Dumb", non esegue fetch di dati ma riceve handler e stato dal genitore (Dashboard).
 */
import React from 'react';
import ChatLLM from '../assistant/ChatLLM';
import TaskHistory from '../clinical/TaskHistory';

export default function RightSidebar({ 
  isSidebarOpen, 
  setIsSidebarOpen, 
  activeSidebarTab, 
  setActiveSidebarTab, 
  isAnalyzing, 
  handleAnalysisFinished, 
  handleHistoryTaskClick,
  theme, 
  prediction,
  refreshHistoryTrigger,
  selectedTaskId
}) {
  
  const isDark = theme === 'dark';
  const sidebarContainerClass = isDark ? 'bg-slate-900 border-slate-800' : 'bg-slate-50 border-slate-200';
  const tabHeaderClass = isDark ? 'bg-slate-800 border-slate-700' : 'bg-slate-100/50 border-slate-200';
  
  const activeTabClass = isDark 
    ? 'bg-slate-700 text-blue-400 shadow-sm' 
    : 'bg-white text-blue-600 shadow-sm border border-slate-200';
    
  const inactiveTabClass = isDark 
    ? 'text-slate-400 hover:bg-slate-700/50' 
    : 'text-slate-500 hover:text-slate-700';

  return (
    <div className={`relative h-full transition-all duration-300 ease-in-out ${isSidebarOpen ? 'w-1/3' : 'w-0'}`}>
      
      {/* Bottone Toggle Sidebar */}
      <button 
        onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
        className={`absolute top-6 -left-10 z-40 flex h-10 w-10 items-center justify-center rounded-l-xl border border-r-0 shadow-sm transition-colors ${
          isDark 
          ? 'bg-slate-800 border-slate-700 text-slate-400 hover:text-blue-400' 
          : 'bg-white border-slate-200 text-slate-500 hover:text-blue-600'
        }`}
        aria-label={isSidebarOpen ? "Chiudi Sidebar" : "Apri Sidebar"}
      >
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          {isSidebarOpen ? <path d="m9 18 6-6-6-6" /> : <path d="m15 18-6-6 6-6" />}
        </svg>
      </button>

      {/* Corpo della Sidebar */}
      <aside className={`w-full h-full border-l flex flex-col overflow-hidden transition-colors ${sidebarContainerClass}`}>
        
        {/* Intestazione Tab */}
        {isSidebarOpen && (
          <div className={`flex border-b p-1 z-10 w-full min-w-[320px] ${tabHeaderClass}`}>
            <button 
              onClick={() => setActiveSidebarTab('chat')} 
              className={`flex-1 px-4 py-3 text-xs font-bold rounded-xl transition-all ${
                activeSidebarTab === 'chat' ? activeTabClass : inactiveTabClass
              }`}
            >
              💬 Chat LLM
            </button>
            <button 
              onClick={() => setActiveSidebarTab('history')} 
              className={`flex-1 px-4 py-3 text-xs font-bold rounded-xl transition-all ${
                activeSidebarTab === 'history' ? activeTabClass : inactiveTabClass
              }`}
            >
              📋 Storico Analisi
            </button>
          </div>
        )}

        {/* Contenuto Dinamico Tab */}
        <div className="flex-1 overflow-hidden">
          <div className="h-full w-full min-w-[320px]">
            {activeSidebarTab === 'chat' ? (
              <ChatLLM 
                isAnalyzing={isAnalyzing} 
                theme={theme} 
                prediction={prediction} 
                taskId={selectedTaskId}
              />
            ) : (
              <TaskHistory 
                onTaskCompleted={handleAnalysisFinished} 
                onTaskClick={handleHistoryTaskClick} 
                theme={theme} 
                refreshHistoryTrigger={refreshHistoryTrigger} 
              /> 
            )}
          </div>
        </div>
      </aside>
    </div>
  );
}