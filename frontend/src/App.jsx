import React, { useState } from 'react';

import Header from './components/layout/Header';
import UploadZone from './components/clinical/UploadZone';
import ClinicalViewer from './components/clinical/Viewer';
import ChatLLM from './components/assistant/ChatLLM';

export default function App() {
  const [activeTab, setActiveTab] = useState('3d');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const selectedExperiment = 'FTD-Study-2024';
  
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');
  
  // Nuovo stato per gestire l'apertura/chiusura della sidebar LLM
  const [isChatOpen, setIsChatOpen] = useState(true);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadStatus('idle');
    }
  };

  const uploadFile = async () => {
    if (!file) return;
    setUploadStatus('uploading');
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await fetch('http://localhost:8000/upload', { method: 'POST', body: formData });
      setUploadStatus(response.ok ? 'success' : 'error');
    } catch {
      setUploadStatus('error');
    }
  };

  const handleStartAnalysis = async () => {
    if (uploadStatus !== 'success') return;
    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ experiment: selectedExperiment, filename: file.name })
      });
      if (response.ok) setActiveTab('umap');
    } catch (error) {
      console.error("Errore analisi:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="h-screen w-full bg-clinical-bg text-slate-900 flex flex-col font-sans overflow-hidden">
      <Header experiment={selectedExperiment} />
      
      <main className="flex-1 flex overflow-hidden">
        
        {/* Usando flex-1, quest'area si espande automaticamente quando la chat si chiude */}
        <section className="flex-1 flex flex-col p-6 gap-6 overflow-y-auto transition-all duration-300">
          <UploadZone file={file} uploadStatus={uploadStatus} onFileChange={handleFileChange} onUpload={uploadFile} />
          
          <ClinicalViewer file={file} activeTab={activeTab} setActiveTab={setActiveTab} isAnalyzing={isAnalyzing} />
          
          {/* Action Bar */}
          <div className="flex justify-between items-center bg-clinical-surface p-5 rounded-2xl border border-clinical-border shadow-clinical-sm">
            <div className="flex items-center gap-3">
               <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter ${uploadStatus === 'success' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-clinical-bg text-clinical-secondary border border-clinical-border'}`}>
                <div className={`w-2 h-2 rounded-full ${uploadStatus === 'success' ? 'bg-clinical-success' : 'bg-slate-300'}`}></div>
                {uploadStatus === 'success' ? "Paziente Caricato" : "Sistema in Attesa"}
              </div>
            </div>
            <button 
              onClick={handleStartAnalysis} disabled={isAnalyzing || uploadStatus !== 'success'}
              className="px-10 py-4 bg-clinical-primary hover:opacity-95 disabled:bg-slate-100 disabled:text-slate-300 rounded-xl font-bold text-white transition-all shadow-lg shadow-blue-200 active:scale-95"
            >
              {isAnalyzing ? "Analisi in Corso..." : "AVVIA DIAGNOSI DIFFERENZIALE"}
            </button>
          </div>
        </section>

        {/* Colonna Destra (Chat LLM Collapsable) */}
        <aside 
          className={`relative flex flex-col bg-clinical-surface transition-all duration-300 ease-in-out border-clinical-border ${
            isChatOpen ? 'w-1/3 border-l' : 'w-0 border-l-0'
          }`}
        >
          <button
            onClick={() => setIsChatOpen(!isChatOpen)}
            aria-label={isChatOpen ? "Nascondi Assistente" : "Mostra Assistente"}
            className="absolute top-6 -left-10 z-20 flex h-10 w-10 items-center justify-center rounded-l-xl border border-r-0 border-clinical-border bg-clinical-surface shadow-[-4px_4px_10px_rgba(0,0,0,0.05)] hover:bg-slate-50 active:scale-95 transition-all text-slate-500 hover:text-clinical-primary"
          >
            {isChatOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m9 18 6-6-6-6"/>
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="m15 18-6-6 6-6"/>
              </svg>
            )}
          </button>

          <div className="flex-1 overflow-hidden">
            <div className="h-full w-full min-w-[320px]">
              <ChatLLM isAnalyzing={isAnalyzing} experiment={selectedExperiment} />
            </div>
          </div>
        </aside>

      </main>
    </div>
  );
}