/*
  L'area di lavoro privata del medico.
*/
import React, { useState, useContext } from 'react';

import Header from '../components/layout/Header';
import UploadZone from '../components/clinical/UploadZone';
import ClinicalViewer from '../components/viewers/Viewer';
import ChatLLM from '../components/assistant/ChatLLM';
import TaskHistory from '../components/clinical/TaskHistory';

import { AuthContext } from '../contexts/AuthContext';

export default function Dashboard() {
  const { token } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('3d');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const selectedExperiment = 'FTD-Study-2024';

  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [currentTaskStatus, setCurrentTaskStatus] = useState(null);

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeSidebarTab, setActiveSidebarTab] = useState('chat');

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadStatus('idle');
      setCurrentTaskStatus(null); // Reset
    }
  };

  const uploadFile = async () => {
    if (!file) return;
    setUploadStatus('uploading');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/analyze/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus('success');
        setCurrentTaskStatus(data.status); // PENDING

        setActiveSidebarTab('history');
        setIsSidebarOpen(true);

      } else {
        setUploadStatus('error');
      }
    } catch {
      setUploadStatus('error');
    }
  };

  const handleStartAnalysis = async () => {
    // Al momento questo bottone "finge" l'analisi visiva. 
    // In futuro a Nextflow.
    if (uploadStatus !== 'success') return;
    setIsAnalyzing(true);

    // Simuliamo un'attesa per la UI
    setTimeout(() => {
      setIsAnalyzing(false);
      setActiveTab('umap');
    }, 2000);
  };

  return (
    <div className="h-screen w-full bg-clinical-bg text-slate-900 flex flex-col font-sans overflow-hidden">
      <Header experiment={selectedExperiment} />

      <main className="flex-1 flex overflow-hidden">

        <section className="flex-1 flex flex-col p-6 gap-6 overflow-y-auto transition-all duration-300">
          <UploadZone file={file} uploadStatus={uploadStatus} onFileChange={handleFileChange} onUpload={uploadFile} />

          <ClinicalViewer file={file} activeTab={activeTab} setActiveTab={setActiveTab} isAnalyzing={isAnalyzing} />

          {/* Action Bar (Il nostro Cardiomonitor) */}
          <div className="flex justify-between items-center bg-clinical-surface p-5 rounded-2xl border border-clinical-border shadow-clinical-sm">
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter ${uploadStatus === 'success' ? 'bg-amber-100 text-amber-700 border border-amber-200' :
                  'bg-clinical-bg text-clinical-secondary border border-clinical-border'
                }`}>
                <div className={`w-2 h-2 rounded-full ${uploadStatus === 'success' ? 'bg-amber-500 animate-pulse' : 'bg-slate-300'
                  }`}></div>

                {/* Logica del testo del monitor */}
                {uploadStatus === 'idle' && "Sistema in Attesa"}
                {uploadStatus === 'uploading' && "Caricamento Rete..."}
                {uploadStatus === 'success' && currentTaskStatus === 'PENDING' && "In Coda (Pending)"}
                {uploadStatus === 'error' && "Errore di Rete"}

              </div>
            </div>

            <button
              onClick={handleStartAnalysis} disabled={isAnalyzing || uploadStatus !== 'success'}
              className="px-10 py-4 bg-clinical-primary hover:opacity-95 disabled:bg-slate-100 disabled:text-slate-300 rounded-xl font-bold text-white transition-all shadow-lg shadow-blue-200 active:scale-95"
            >
              {isAnalyzing ? "Elaborazione in Corso..." : "AVVIA DIAGNOSI DIFFERENZIALE"}
            </button>
          </div>
        </section>

        {/* Colonna Destra (Sidebar con Tabs) */}
        <aside
          className={`relative flex flex-col bg-clinical-surface transition-all duration-300 ease-in-out border-clinical-border ${isSidebarOpen ? 'w-1/3 border-l' : 'w-0 border-l-0'
            }`}
        >
          {/* Bottone Toggle (freccina) - Rimasto Invariato */}
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            aria-label={isSidebarOpen ? "Nascondi Sidebar" : "Mostra Sidebar"}
            className="absolute top-6 -left-10 z-20 flex h-10 w-10 items-center justify-center rounded-l-xl border border-r-0 border-clinical-border bg-clinical-surface shadow-[-4px_4px_10px_rgba(0,0,0,0.05)] hover:bg-slate-50 active:scale-95 transition-all text-slate-500 hover:text-clinical-primary"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isSidebarOpen ? <path d="m9 18 6-6-6-6" /> : <path d="m15 18-6-6 6-6" />}
            </svg>
          </button>

          {/* I TABS (Solo visibili se aperta) */}
          {isSidebarOpen && (
            <div className="flex border-b border-clinical-border bg-slate-50/50 p-1 z-10 w-full min-w-[320px]">
              <button
                onClick={() => setActiveSidebarTab('chat')}
                className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeSidebarTab === 'chat' ? 'bg-white text-clinical-primary shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}
              >
                💬 Chat LLM
              </button>
              <button
                onClick={() => setActiveSidebarTab('history')}
                className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeSidebarTab === 'history' ? 'bg-white text-clinical-primary shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}
              >
                📋 Storico Analisi
              </button>
            </div>
          )}

          <div className="flex-1 overflow-hidden">
            <div className="h-full w-full min-w-[320px]">
              {/* Rendering Condizionale basato sul Tab attivo */}
              {activeSidebarTab === 'chat' ? (
                <ChatLLM isAnalyzing={isAnalyzing} experiment={selectedExperiment} />
              ) : (
                <TaskHistory />
              )}
            </div>
          </div>
        </aside>

      </main>
    </div>
  );
}