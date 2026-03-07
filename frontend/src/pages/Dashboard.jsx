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
  const [niftiUrl, setNiftiUrl] = useState(null); // <-- NUOVO STATO: per il NIfTI scaricato dalla rete
  
  const [uploadStatus, setUploadStatus] = useState('idle');
  const [currentTaskStatus, setCurrentTaskStatus] = useState(null);

  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeSidebarTab, setActiveSidebarTab] = useState('chat');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedModel, setSelectedModel] = useState('HC_vs_bvFTD'); 
  const [umapData, setUmapData] = useState(null);
  const [prediction, setPrediction] = useState(null);

  // GESTIONE NUOVO UPLOAD (File Locale)
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setNiftiUrl(null); // Resettiamo l'URL di rete se carichiamo un file locale
      setUploadStatus('idle');
      setCurrentTaskStatus(null);
      setUmapData(null);
      setPrediction(null);
      setActiveTab('3d');
    }
  };

  const handleConfirmClick = () => {
    if (!file) return;
    setIsModalOpen(true);
  };

  const executeUploadAndAnalyze = async () => {
    setIsModalOpen(false);
    setUploadStatus('uploading');
    setIsAnalyzing(true);

    const formData = new FormData();
    formData.append('file', file);
    formData.append('model_name', selectedModel); 

    try {
      const response = await fetch('http://localhost:8000/analyze/', {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}` },
        body: formData
      });

      if (response.ok) {
        const data = await response.json();
        setUploadStatus('success');
        setCurrentTaskStatus(data.status);
        setActiveSidebarTab('history');
        setIsSidebarOpen(true);
      } else {
        setUploadStatus('error');
        setIsAnalyzing(false);
      }
    } catch {
      setUploadStatus('error');
      setIsAnalyzing(false);
    }
  };

  // CALLBACK: Fine Polling
  const handleAnalysisFinished = (data, taskMeta) => {
    setUmapData(data.plot_data);
    const predizioneSicura = Array.isArray(data.diagnosi_predetta) ? data.diagnosi_predetta[0] : data.diagnosi_predetta;
    setPrediction(predizioneSicura);
    
    // Aggiorniamo la UI al modello appena usato (estraendo 'bvFTD' da 'HC_vs_bvFTD')
    if (taskMeta && taskMeta.model_name) {
       setSelectedModel(taskMeta.model_name);
    }

    setIsAnalyzing(false);
    setActiveTab('umap');
  };

  // --- NUOVO: CALLBACK QUANDO SI CLICCA UNA CARD NELLO STORICO ---
  const handleHistoryTaskClick = (storicoData) => {
    console.log("📥 Caricamento paziente dallo storico:", storicoData);
    
    setFile(null); // Rimuoviamo il file locale
    setNiftiUrl(storicoData.niftiUrl); // Impostiamo l'URL di rete fornito da FastAPI
    
    setUmapData(storicoData.umapData);
    const predizioneSicura = Array.isArray(storicoData.prediction) ? storicoData.prediction[0] : storicoData.prediction;
    setPrediction(predizioneSicura);
    
    // Sincronizziamo il tab del Radar Locale col modello usato storicamente
    if (storicoData.modelName) {
       setSelectedModel(storicoData.modelName); 
    }

    setUploadStatus('success');
    setIsAnalyzing(false);
    setActiveTab('umap'); // Portiamo il medico subito sul radar
  };

  return (
    <div className="h-screen w-full bg-clinical-bg text-slate-900 flex flex-col font-sans overflow-hidden relative">
      <Header experiment={selectedExperiment} />

      {/* MODALE OVERLAY */}
      {isModalOpen && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white p-8 rounded-2xl shadow-2xl w-[450px] flex flex-col gap-6 animate-in fade-in zoom-in duration-200">
            <div>
              <h3 className="text-2xl font-bold text-slate-800">Sospetto Clinico</h3>
              <p className="text-sm text-slate-500 mt-1">Seleziona il modello diagnostico da applicare:</p>
            </div>
            <div className="flex flex-col gap-3">
              {['HC_vs_bvFTD', 'HC_vs_svPPA', 'HC_vs_nfvPPA'].map(m => (
                 <label key={m} className={`flex items-center gap-3 cursor-pointer p-4 rounded-xl border-2 transition-all ${selectedModel === m ? 'border-clinical-primary bg-blue-50/50' : 'border-slate-100 hover:border-slate-200 hover:bg-slate-50'}`}>
                    <input type="radio" name="model" value={m} className="w-5 h-5 accent-clinical-primary" checked={selectedModel === m} onChange={(e) => setSelectedModel(e.target.value)} />
                    <span className="font-semibold text-slate-700">{m.replace('HC_vs_', '')} (Variante)</span>
                 </label>
              ))}
            </div>
            <div className="flex justify-end gap-3 mt-2">
              <button onClick={() => setIsModalOpen(false)} className="px-5 py-3 text-slate-600 hover:bg-slate-100 rounded-xl font-bold transition-colors">Annulla</button>
              <button onClick={executeUploadAndAnalyze} className="px-5 py-3 bg-clinical-primary text-white rounded-xl font-bold hover:bg-blue-600 shadow-lg active:scale-95">Conferma e Analizza</button>
            </div>
          </div>
        </div>
      )}

      <main className="flex-1 flex overflow-hidden">
        <section className="flex-1 flex flex-col p-6 gap-6 overflow-y-auto transition-all duration-300">
          
          <UploadZone file={file} uploadStatus={uploadStatus} onFileChange={handleFileChange} onUpload={handleConfirmClick} />

          {/* PASSIAMO SIA IL FILE LOCALE CHE L'URL DI RETE AL VIEWER */}
          <ClinicalViewer 
            file={file} 
            niftiUrl={niftiUrl} 
            activeTab={activeTab} 
            setActiveTab={setActiveTab} 
            isAnalyzing={isAnalyzing} 
            umapData={umapData}        
            prediction={prediction}    
            selectedModel={selectedModel} // Passiamo il modello selezionato per sincronizzare i tab
          />

          <div className="flex justify-between items-center bg-clinical-surface p-5 rounded-2xl border border-clinical-border shadow-clinical-sm">
            <div className="flex items-center gap-3">
              <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter ${uploadStatus === 'success' ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'bg-clinical-bg text-clinical-secondary border border-clinical-border'}`}>
                <div className={`w-2 h-2 rounded-full ${uploadStatus === 'success' ? 'bg-amber-500 animate-pulse' : 'bg-slate-300'}`}></div>
                {uploadStatus === 'idle' && "Sistema in Attesa"}
                {uploadStatus === 'uploading' && "Caricamento Rete..."}
                {uploadStatus === 'success' && currentTaskStatus === 'PENDING' && "In Coda (Pending)"}
                {uploadStatus === 'success' && isAnalyzing && "Elaborazione in Corso"}
                {uploadStatus === 'error' && "Errore di Rete"}
              </div>
            </div>
            <button
              onClick={() => {}} disabled={true} // Disattivato (gestito da UploadZone/Modale)
              className="px-10 py-4 bg-slate-100 text-slate-300 rounded-xl font-bold transition-all"
            >
              PRONTO
            </button>
          </div>
        </section>

        <aside className={`relative flex flex-col bg-clinical-surface transition-all duration-300 ease-in-out border-clinical-border ${isSidebarOpen ? 'w-1/3 border-l' : 'w-0 border-l-0'}`}>
          <button onClick={() => setIsSidebarOpen(!isSidebarOpen)} className="absolute top-6 -left-10 z-20 flex h-10 w-10 items-center justify-center rounded-l-xl border border-r-0 border-clinical-border bg-clinical-surface text-slate-500 hover:text-clinical-primary">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              {isSidebarOpen ? <path d="m9 18 6-6-6-6" /> : <path d="m15 18-6-6 6-6" />}
            </svg>
          </button>

          {isSidebarOpen && (
            <div className="flex border-b border-clinical-border bg-slate-50/50 p-1 z-10 w-full min-w-[320px]">
              <button onClick={() => setActiveSidebarTab('chat')} className={`flex-1 px-4 py-3 text-xs font-bold rounded-xl ${activeSidebarTab === 'chat' ? 'bg-white text-clinical-primary shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}>💬 Chat LLM</button>
              <button onClick={() => setActiveSidebarTab('history')} className={`flex-1 px-4 py-3 text-xs font-bold rounded-xl ${activeSidebarTab === 'history' ? 'bg-white text-clinical-primary shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}>📋 Storico Analisi</button>
            </div>
          )}

          <div className="flex-1 overflow-hidden">
            <div className="h-full w-full min-w-[320px]">
              {activeSidebarTab === 'chat' ? (
                <ChatLLM isAnalyzing={isAnalyzing} experiment={selectedExperiment} />
              ) : (
                <TaskHistory onTaskCompleted={handleAnalysisFinished} onTaskClick={handleHistoryTaskClick} /> 
              )}
            </div>
          </div>
        </aside>

      </main>
    </div>
  );
}