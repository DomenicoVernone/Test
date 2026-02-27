import React, { useState, useRef } from 'react';
import { 
  FileUp, 
  Brain, 
  LineChart, 
  Send, 
  Settings, 
  Activity,
  MessageSquare,
  ChevronDown,
  CheckCircle2,
  User,
  AlertCircle
} from 'lucide-react';

/**
 * APP CLINICAL DIGITAL TWIN
 * Architettura professionale che utilizza i Design Tokens definiti in index.css.
 * Questo file gestisce il layout, lo stato dell'upload e l'interazione con l'LLM.
 */
export default function App() {
  // --- STATI UI ---
  const [activeTab, setActiveTab] = useState('3d'); // Gestisce lo switch tra NiiVue e Plotly
  const [isAnalyzing, setIsAnalyzing] = useState(false); // Stato dell'analisi asincrona
  const selectedExperiment = 'FTD-Study-2024';
  
  // --- STATI DATI ---
  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle'); // 'idle', 'uploading', 'success', 'error'
  const fileInputRef = useRef(null);

  // --- LOGICA DI COMUNICAZIONE ---
  
  // Gestione della selezione file locale
  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setUploadStatus('idle');
    }
  };

  // Funzione di upload verso il backend FastAPI
  const uploadFile = async () => {
    if (!file) return;
    setUploadStatus('uploading');
    
    const formData = new FormData();
    formData.append('file', file);

    try {
      // Nota: Sostituire con l'URL corretto del container se necessario (es. localhost:8000)
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        setUploadStatus('success');
      } else {
        setUploadStatus('error');
      }
    } catch (error) {
      console.error("Errore durante l'upload:", error);
      setUploadStatus('error');
    }
  };

  // Avvio dell'analisi clinica (simula il processo asincrono R + Plotly)
  const handleStartAnalysis = async () => {
    if (uploadStatus !== 'success') return;
    setIsAnalyzing(true);
    
    try {
      // Chiamata all'endpoint /analyze di FastAPI
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ experiment: selectedExperiment, filename: file.name })
      });

      if (response.ok) {
        // Al termine, passiamo automaticamente alla vista dei risultati (Plotly)
        setActiveTab('umap');
      }
    } catch (error) {
      console.error("Errore durante l'analisi:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    // Sfondo principale definito in index.css (clinical-bg)
    <div className="h-screen w-full bg-clinical-bg text-slate-900 flex flex-col font-sans overflow-hidden">
      
      {/* HEADER: Navigazione e Identità Visiva */}
      <header className="h-16 border-b border-clinical-border flex items-center justify-between px-6 bg-clinical-surface shadow-clinical-sm z-10">
        <div className="flex items-center gap-3">
          <div className="bg-clinical-primary p-2 rounded-lg shadow-lg shadow-blue-500/20">
            <Activity className="text-white w-5 h-5" />
          </div>
          <h1 className="text-xl font-bold tracking-tight text-slate-800 uppercase italic">
            Clinical<span className="text-clinical-primary font-black">Twin</span>
          </h1>
        </div>

        <div className="flex items-center gap-6">
          <div className="hidden md:flex flex-col items-end border-r border-clinical-border pr-4">
            <span className="text-[10px] text-clinical-secondary uppercase font-bold tracking-widest text-right">Protocollo Attivo</span>
            <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
              {selectedExperiment}
              <ChevronDown className="w-4 h-4 text-clinical-secondary" />
            </div>
          </div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-clinical-bg border border-clinical-border flex items-center justify-center text-clinical-secondary hover:bg-slate-100 transition-colors cursor-pointer">
              <User className="w-5 h-5" />
            </div>
            <Settings className="w-5 h-5 text-clinical-secondary cursor-pointer hover:text-slate-600" />
          </div>
        </div>
      </header>

      {/* AREA PRINCIPALE: Griglia a due colonne */}
      <main className="flex-1 grid grid-cols-12 overflow-hidden">
        
        {/* COLONNA SINISTRA: INPUT E VISUALIZZAZIONE DATI (65%) */}
        <section className="col-span-8 flex flex-col p-6 gap-6 overflow-y-auto border-r border-clinical-border">
          
          {/* AREA UPLOAD: Gestione dinamica dello stato (Idle, Success, Error) */}
          <div 
            onClick={() => fileInputRef.current.click()}
            className={`relative overflow-hidden bg-clinical-surface border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all cursor-pointer group shadow-clinical-sm
              ${uploadStatus === 'success' ? 'border-clinical-success bg-emerald-50' : 'border-clinical-border hover:border-clinical-primary hover:bg-blue-50/50'}
              ${uploadStatus === 'error' ? 'border-clinical-danger bg-red-50' : ''}
            `}
          >
            <input 
              type="file" 
              ref={fileInputRef} 
              onChange={handleFileChange} 
              className="hidden" 
              accept=".nii,.gz,.dcm"
            />
            
            {uploadStatus === 'success' ? (
              <CheckCircle2 className="w-12 h-12 text-clinical-success" />
            ) : uploadStatus === 'error' ? (
              <AlertCircle className="w-12 h-12 text-clinical-danger" />
            ) : (
              <div className="bg-clinical-bg p-4 rounded-full group-hover:bg-blue-100">
                <FileUp className={`w-8 h-8 ${file ? 'text-clinical-primary' : 'text-slate-300 group-hover:text-clinical-primary'}`} />
              </div>
            )}

            <div className="text-center">
              <p className="text-lg font-bold text-slate-800">
                {file ? file.name : "Carica Esame MRI"}
              </p>
              <p className="text-sm text-clinical-secondary font-medium">
                {file ? `${(file.size / (1024*1024)).toFixed(2)} MB` : "Seleziona file NIfTI (.nii) o DICOM"}
              </p>
            </div>

            {file && uploadStatus !== 'success' && (
              <button 
                onClick={(e) => { e.stopPropagation(); uploadFile(); }}
                className="mt-2 px-8 py-2 bg-clinical-primary text-white rounded-lg font-bold text-sm hover:opacity-95 shadow-clinical-md"
              >
                {uploadStatus === 'uploading' ? "Trasferimento..." : "Conferma Invio"}
              </button>
            )}
          </div>

          {/* VISUALIZZATORE CON SWITCH INTERNO (Tab System) */}
          <div className="flex-1 bg-clinical-surface rounded-2xl border border-clinical-border flex flex-col overflow-hidden shadow-clinical-sm">
            {/* Navigazione Tab */}
            <div className="flex border-b border-clinical-border bg-slate-50/50 p-1">
              <button 
                onClick={() => setActiveTab('3d')}
                className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeTab === '3d' ? 'bg-clinical-surface text-clinical-primary shadow-clinical-sm border border-clinical-border' : 'text-clinical-secondary hover:text-slate-600'}`}
              >
                <Brain className="w-4 h-4" /> RICOSTRUZIONE ANATOMICA
              </button>
              <button 
                onClick={() => setActiveTab('umap')}
                className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeTab === 'umap' ? 'bg-clinical-surface text-clinical-primary shadow-clinical-sm border border-clinical-border' : 'text-clinical-secondary hover:text-slate-600'}`}
              >
                <LineChart className="w-4 h-4" /> SPAZIO LATENTE (UMAP)
              </button>
            </div>

            {/* Area Contenuto Dinamico: Qui si alterneranno NiiVue e Plotly */}
            <div className="flex-1 flex items-center justify-center relative bg-slate-100/20">
              {isAnalyzing ? (
                <div className="flex flex-col items-center gap-4 text-center">
                  <div className="h-10 w-10 border-4 border-clinical-primary/20 border-t-clinical-primary rounded-full animate-spin"></div>
                  <div>
                    <p className="text-[10px] font-bold text-clinical-secondary uppercase tracking-[0.3em]">Elaborazione in corso</p>
                    <p className="text-[9px] text-slate-400 italic">Segmentazione volumetrica e proiezione spazio latente...</p>
                  </div>
                </div>
              ) : (
                <div className="text-center p-10">
                  <Activity className="w-12 h-12 mx-auto mb-4 text-slate-200" />
                  <p className="text-clinical-secondary italic text-sm font-medium">
                    {activeTab === '3d' 
                      ? "In attesa del segnale anatomico NIfTI..." 
                      : "I cluster UMAP verranno generati al termine dell'analisi."}
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* BARRA DELLE AZIONI INFERIORE */}
          <div className="flex justify-between items-center bg-clinical-surface p-5 rounded-2xl border border-clinical-border shadow-clinical-sm">
            <div className="flex items-center gap-3">
               <div className={`flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-tighter ${uploadStatus === 'success' ? 'bg-emerald-100 text-emerald-700 border border-emerald-200' : 'bg-clinical-bg text-clinical-secondary border border-clinical-border'}`}>
                <div className={`w-2 h-2 rounded-full ${uploadStatus === 'success' ? 'bg-clinical-success' : 'bg-slate-300'}`}></div>
                {uploadStatus === 'success' ? "Paziente Caricato" : "Sistema in Attesa"}
              </div>
            </div>
            <button 
              onClick={handleStartAnalysis}
              disabled={isAnalyzing || uploadStatus !== 'success'}
              className="px-10 py-4 bg-clinical-primary hover:opacity-95 disabled:bg-slate-100 disabled:text-slate-300 rounded-xl font-bold text-white transition-all shadow-lg shadow-blue-200 active:scale-95"
            >
              {isAnalyzing ? "Analisi in Corso..." : "AVVIA DIAGNOSI DIFFERENZIALE"}
            </button>
          </div>
        </section>

        {/* COLONNA DESTRA: ASSISTENTE CLINICO (35%) */}
        <section className="col-span-4 bg-clinical-surface flex flex-col overflow-hidden border-l border-clinical-border">
          <div className="p-6 border-b border-clinical-border bg-slate-50/20 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <MessageSquare className="w-5 h-5 text-clinical-primary" />
              <h2 className="font-bold text-slate-800 tracking-tight">Clinical Assistant</h2>
            </div>
            <span className="text-[9px] bg-clinical-primary/10 text-clinical-primary px-2 py-1 rounded font-bold uppercase tracking-widest border border-blue-100">AI Support</span>
          </div>

          {/* Cronologia della Chat */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
            <div className="bg-clinical-bg p-5 rounded-2xl rounded-tl-none border border-clinical-border shadow-clinical-sm">
              <p className="text-sm leading-relaxed text-slate-700">
                Benvenuto, Dottore. Sono pronto ad assisterla nella valutazione del caso confrontando il profilo del paziente con il database <span className="font-bold">{selectedExperiment}</span>.
              </p>
            </div>
            
            {isAnalyzing && (
              <div className="flex items-center gap-2 text-clinical-primary italic text-[11px] animate-pulse font-medium">
                <Brain className="w-4 h-4" /> Elaborazione insight diagnostici...
              </div>
            )}
          </div>

          {/* AREA INPUT CHAT: Design pulito e funzionale */}
          <div className="p-6 border-t border-clinical-border bg-slate-50/10">
            <div className="relative group">
              <input 
                type="text" 
                placeholder="Chiedi un'interpretazione..."
                className="w-full bg-clinical-surface border border-clinical-border rounded-xl py-4 pl-5 pr-14 text-sm focus:outline-none focus:border-clinical-primary shadow-inner"
              />
              <button className="absolute right-3 top-1/2 -translate-y-1/2 bg-clinical-primary text-white p-2 rounded-lg hover:opacity-90 shadow-clinical-md transition-all">
                <Send className="w-4 h-4" />
              </button>
            </div>
            <p className="text-[9px] text-slate-400 mt-4 text-center font-medium leading-tight italic">
              Supporto Diagnostico Digitale. Verificare sempre i dati grezzi NIfTI.
            </p>
          </div>
        </section>

      </main>
    </div>
  );
}