/**
 * Componente Contenitore della Visualizzazione Clinica.
 * Gestisce l'alternanza visiva tra la ricostruzione anatomica 3D (NiiVue) 
 * e la proiezione nello spazio latente (UMAP Plotly).
 *
 * @param {Object} props
 * @param {File|null} props.file - File locale caricato.
 * @param {string|null} props.niftiUrl - URL del file nello storico.
 * @param {string} props.activeTab - Tab attivo ('3d' o 'umap').
 * @param {Function} props.setActiveTab - Setter per il tab attivo.
 * @param {boolean} props.isAnalyzing - Stato di caricamento (spinner).
 * @param {Object|null} props.umapData - JSON con le coordinate UMAP calcolate in R.
 * @param {string} props.selectedModel - Nome del modello AI in uso.
 * @param {string} props.colorMap - Mappa colori per il NIfTI.
 * @param {string} props.theme - Tema grafico ('light' o 'dark').
 */
import React from 'react';
import { Brain, LineChart, Activity } from 'lucide-react';
import NiiVueCanvas from './NiiVue';
import UmapPlot from './UmapPlot';

const ClinicalViewer = ({ file, niftiUrl, activeTab, setActiveTab, isAnalyzing, umapData, selectedModel, colorMap, theme }) => {
  
  // Costanti per pulizia visiva delle classi Tailwind
  const isDark = theme === 'dark';
  const containerClass = isDark ? 'bg-slate-900 border-slate-700 text-slate-100' : 'bg-white border-slate-200 text-slate-900';
  const headerClass = isDark ? 'border-slate-700 bg-slate-800' : 'border-slate-200 bg-slate-50';
  
  const activeBtnClass = isDark 
    ? 'bg-slate-700 text-blue-400 shadow-sm border border-slate-600' 
    : 'bg-white text-clinical-primary shadow-sm border border-slate-200';
  const inactiveBtnClass = isDark 
    ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50' 
    : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100/50';

  return (
    <div className={`flex-1 rounded-2xl border flex flex-col overflow-hidden shadow-sm transition-colors duration-300 ${containerClass}`}>
      
      {/* BARRA SUPERIORE */}
      <div className={`flex border-b p-1 z-10 transition-colors ${headerClass}`}>
        <button
          onClick={() => setActiveTab('3d')}
          className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeTab === '3d' ? activeBtnClass : inactiveBtnClass}`}
        >
          <Brain className="w-4 h-4" /> VISUALIZZATORE MULTIPLANARE (MPR)
        </button>
        <button
          onClick={() => setActiveTab('umap')}
          className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeTab === 'umap' ? activeBtnClass : inactiveBtnClass}`}
        >
          <LineChart className="w-4 h-4" /> SPAZIO LATENTE (UMAP)
        </button>
      </div>

      {/* AREA CONTENUTO */}
      <div className={`flex-1 flex flex-col relative overflow-hidden transition-colors ${isDark ? 'bg-slate-900/50' : 'bg-slate-50/30'}`}>
        
        {activeTab === '3d' ? (
          /* TAB 1: RICOSTRUZIONE 3D (Sempre visibile se c'è un file) */
          (file || niftiUrl) ? (
            <NiiVueCanvas file={file} niftiUrl={niftiUrl} colorMap={colorMap} />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-10 z-10 text-center">
              <Activity className={`w-12 h-12 mx-auto mb-4 ${isDark ? 'text-slate-600' : 'text-slate-300'}`} />
              <p className={`italic text-sm font-medium ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                In attesa del segnale anatomico NIfTI...
              </p>
            </div>
          )
        ) : (
          /* TAB 2: SPAZIO LATENTE (Mostra lo spinner se in elaborazione) */
          isAnalyzing ? (
            <div className={`absolute inset-0 flex flex-col items-center justify-center gap-4 text-center z-10 backdrop-blur-sm transition-colors ${isDark ? 'bg-slate-900/80' : 'bg-white/80'}`}>
              <div className="h-10 w-10 border-4 border-clinical-primary/20 border-t-clinical-primary rounded-full animate-spin"></div>
              <div>
                <p className="text-[10px] font-bold text-clinical-secondary uppercase tracking-[0.3em]">Elaborazione in corso</p>
                <p className={`text-[9px] italic ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                  Segmentazione volumetrica e proiezione spazio latente...
                </p>
              </div>
            </div>
          ) : umapData ? (
            <div className={`flex-1 w-full h-full relative p-2 transition-colors ${isDark ? 'bg-slate-900' : 'bg-white'}`}>
              <UmapPlot data={umapData} selectedModel={selectedModel} theme={theme} />
            </div>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <Activity className={`w-12 h-12 mx-auto mb-4 ${isDark ? 'text-slate-600' : 'text-slate-300'}`} />
              <p className={`italic text-sm font-medium ${isDark ? 'text-slate-400' : 'text-slate-500'}`}>
                I cluster UMAP verranno generati al termine dell'analisi.
              </p>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default ClinicalViewer;