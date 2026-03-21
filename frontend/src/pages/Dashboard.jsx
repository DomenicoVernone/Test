/**
 * L'area di lavoro privata del medico.
 * Orchesta il caricamento del file NIfTI, la selezione del modello,
 * la visualizzazione 3D/UMAP e l'integrazione con l'Assistente AI.
 */
import React, { useState } from 'react';
import SettingsModal from '../components/layout/SettingsModal';
import Header from '../components/layout/Header';
import UploadZone from '../components/clinical/UploadZone';
import ClinicalViewer from '../components/viewers/Viewer';
import RightSidebar from '../components/layout/RightSidebar';
import { orchestratorApi } from '../services/api';


export default function Dashboard() {
  
  // --- STATI DATI ---
  const [file, setFile] = useState(null); // Tiene il PRIMO file per l'anteprima 3D
  const [files, setFiles] = useState([]); // Array di tutti i file selezionati per il batch
  const [niftiUrl, setNiftiUrl] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('idle');

  // --- STATI UI ---
  const [activeTab, setActiveTab] = useState('3d');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [refreshHistoryTrigger, setRefreshHistoryTrigger] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [activeSidebarTab, setActiveSidebarTab] = useState('chat');

  // --- STATI MODALI E SETTINGS ---
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [colorMap, setColorMap] = useState('gray'); 
  const [theme, setTheme] = useState('light'); 

  // --- STATI MODELLO E INFERENZA ---
  const [selectedModel, setSelectedModel] = useState('HC_vs_bvFTD');
  const [umapData, setUmapData] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [currentTaskId, setCurrentTaskId] = useState(null); 

  // --- HANDLERS ---
  const handleFileChange = (event) => {
    const selectedFiles = Array.from(event.target.files);
    
    if (selectedFiles.length > 0) {
      setFiles(selectedFiles); 
      setFile(selectedFiles[0]); 
      
      setNiftiUrl(null);
      setUploadStatus('idle');
      setUmapData(null);
      setPrediction(null);
      setCurrentTaskId(null);
      setActiveTab('3d');
    }
  };
  const handleClearSelection = () => {
    setFile(null);
    setFiles([]); 
  };

  const handleConfirmClick = () => {
    if (files.length === 0) return;
    setIsModalOpen(true);
  };

  const executeUploadAndAnalyze = async () => {
    setIsModalOpen(false);
    setUploadStatus('uploading');
    setIsAnalyzing(true);

    try {
      const uploadPromises = files.map(currentFile => {
        const formData = new FormData();
        formData.append('file', currentFile);
        formData.append('model_name', selectedModel);
        
        return orchestratorApi.post('/analyze/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
      });

      await Promise.all(uploadPromises);

      setUploadStatus('success');
      setRefreshHistoryTrigger(prev => prev + 1);
      setActiveSidebarTab('history');
      setIsSidebarOpen(true);
      
      setFiles([]); 
      
    } catch (error) {
      console.error("🚨 Errore durante l'upload e analisi:", error);
      setUploadStatus('error');
      setIsAnalyzing(false);
    }
  };

  const handleAnalysisFinished = (data, taskMeta) => {
    setUmapData(data.plot_data);
    const predizioneSicura = Array.isArray(data.diagnosi_predetta)
      ? data.diagnosi_predetta[0]
      : data.diagnosi_predetta;
    setPrediction(predizioneSicura);

    if (taskMeta && taskMeta.model_name) {
      setSelectedModel(taskMeta.model_name);
    }
    
    // Salviamo l'ID del task appena completato, estraendolo dai metadati
    if (taskMeta && taskMeta.id) {
        setCurrentTaskId(taskMeta.id);
    }

    setIsAnalyzing(false);
    setActiveTab('umap');
  };

  const handleHistoryTaskClick = (storicoData) => {
    console.log("Dati grezzi cliccati dallo storico:", storicoData);
    setFile(null);
    setNiftiUrl(storicoData.niftiUrl);
    setUmapData(storicoData.umapData);
    
    const predizioneSicura = Array.isArray(storicoData.prediction)
      ? storicoData.prediction[0]
      : storicoData.prediction;
    setPrediction(predizioneSicura);

    if (storicoData.modelName) {
      setSelectedModel(storicoData.modelName);
    }
    
    if (storicoData.taskId || storicoData.id) {
      setCurrentTaskId(storicoData.taskId || storicoData.id);
    }

    // GESTIONE UX: Controlliamo se il task è ancora in corso
    const isStillRunning = storicoData.status !== 'COMPLETED';
    
    setIsAnalyzing(isStillRunning); 
    
    // Altrimenti, se ha finito, apriamo direttamente il grafico UMAP.
    setActiveTab(isStillRunning ? '3d' : 'umap');
  };

  // --- RENDER ---
  return (
    <div className={`h-screen w-full flex flex-col font-sans overflow-hidden relative transition-colors duration-300 ${theme === 'dark' ? 'bg-slate-900 text-slate-100' : 'bg-clinical-bg text-slate-900'}`}>

      <Header onOpenSettings={() => setIsSettingsOpen(true)} theme={theme} />
      
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        colorMap={colorMap}
        setColorMap={setColorMap}
        theme={theme}
        setTheme={setTheme}
      />

      {isModalOpen && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
          <div className="bg-white p-8 rounded-2xl shadow-2xl w-112.5 flex flex-col gap-6 animate-in fade-in zoom-in duration-200 text-slate-900">
            <div>
              <h3 className="text-2xl font-bold text-slate-800">Sospetto Clinico</h3>
              <p className="text-sm text-clinical-primary font-semibold mt-1">
                Stai avviando l'analisi per {files.length} {files.length === 1 ? 'paziente' : 'pazienti'}.
              </p>
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
          <UploadZone
            file={file}
            files={files} 
            uploadStatus={uploadStatus}
            onFileChange={handleFileChange}
            onFileSelect={setFile} 
            onUpload={handleConfirmClick}
            onClear={handleClearSelection} 
            theme={theme}
          />
          <ClinicalViewer 
            file={file} 
            niftiUrl={niftiUrl} 
            activeTab={activeTab} 
            setActiveTab={setActiveTab} 
            isAnalyzing={isAnalyzing} 
            umapData={umapData}        
            selectedModel={selectedModel} 
            colorMap={colorMap} 
            theme={theme} 
          />
        </section>

        <RightSidebar 
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          activeSidebarTab={activeSidebarTab}
          setActiveSidebarTab={setActiveSidebarTab}
          isAnalyzing={isAnalyzing}
          handleAnalysisFinished={handleAnalysisFinished}
          handleHistoryTaskClick={handleHistoryTaskClick}
          theme={theme}
          prediction={prediction}
          refreshHistoryTrigger={refreshHistoryTrigger} 
          selectedTaskId={currentTaskId}
        />
      </main>
    </div>
  );
}