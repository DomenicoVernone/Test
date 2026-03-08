import React from 'react';
import { Brain, LineChart, Activity } from 'lucide-react';
import NiiVueCanvas from './NiiVue';
import UmapPlot from './UmapPlot';

const ClinicalViewer = ({ file, niftiUrl, activeTab, setActiveTab, isAnalyzing, umapData, selectedModel, colorMap, theme }) => {

  return (
    <div className={`flex-1 rounded-2xl border flex flex-col overflow-hidden shadow-sm transition-colors duration-300 ${
      theme === 'dark' ? 'bg-slate-900 border-slate-700 text-slate-100' : 'bg-white border-slate-200 text-slate-900'
    }`}>

      {/* BARRA SUPERIORE */}
      <div className={`flex border-b p-1 z-10 transition-colors ${theme === 'dark' ? 'border-slate-700 bg-slate-800' : 'border-slate-200 bg-slate-50'}`}>
        <button
          onClick={() => setActiveTab('3d')}
          className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${
            activeTab === '3d' 
              ? (theme === 'dark' ? 'bg-slate-700 text-blue-400 shadow-sm border border-slate-600' : 'bg-white text-clinical-primary shadow-sm border border-slate-200') 
              : (theme === 'dark' ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100/50')
          }`}
        >
          <Brain className="w-4 h-4" /> RICOSTRUZIONE ANATOMICA
        </button>
        <button
          onClick={() => setActiveTab('umap')}
          className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${
            activeTab === 'umap' 
              ? (theme === 'dark' ? 'bg-slate-700 text-blue-400 shadow-sm border border-slate-600' : 'bg-white text-clinical-primary shadow-sm border border-slate-200') 
              : (theme === 'dark' ? 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50' : 'text-slate-500 hover:text-slate-700 hover:bg-slate-100/50')
          }`}
        >
          <LineChart className="w-4 h-4" /> SPAZIO LATENTE (UMAP)
        </button>
      </div>

      <div className={`flex-1 flex flex-col relative overflow-hidden transition-colors ${theme === 'dark' ? 'bg-slate-900/50' : 'bg-slate-50/30'}`}>

        {isAnalyzing ? (
          <div className={`absolute inset-0 flex flex-col items-center justify-center gap-4 text-center z-10 backdrop-blur-sm transition-colors ${theme === 'dark' ? 'bg-slate-900/80' : 'bg-white/80'}`}>
            <div className="h-10 w-10 border-4 border-clinical-primary/20 border-t-clinical-primary rounded-full animate-spin"></div>
            <div>
              <p className="text-[10px] font-bold text-clinical-secondary uppercase tracking-[0.3em]">Elaborazione in corso</p>
              <p className={`text-[9px] italic ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Segmentazione volumetrica e proiezione spazio latente...</p>
            </div>
          </div>
        ) :

          activeTab === '3d' ? (
            (file || niftiUrl) ? (
              <NiiVueCanvas file={file} niftiUrl={niftiUrl} colorMap={colorMap} />
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center p-10 z-10 text-center">
                <Activity className={`w-12 h-12 mx-auto mb-4 ${theme === 'dark' ? 'text-slate-600' : 'text-slate-300'}`} />
                <p className={`italic text-sm font-medium ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>In attesa del segnale anatomico NIfTI...</p>
              </div>
            )
          ) :

            (
              /* LAYOUT UMAP: MASSIMIZZATO AL 100% DELLO SPAZIO DISPONIBILE */
              umapData ? (
                <div className={`flex-1 w-full h-full relative p-2 transition-colors ${theme === 'dark' ? 'bg-slate-900' : 'bg-white'}`}>
                  {/* Il Plotly ha già sfondo trasparente, quindi prenderà il bg-slate-900 automaticamente! */}
                  <UmapPlot data={umapData} selectedModel={selectedModel} theme={theme} />
                </div>
              ) : (
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <Activity className={`w-12 h-12 mx-auto mb-4 ${theme === 'dark' ? 'text-slate-600' : 'text-slate-300'}`} />
                  <p className={`italic text-sm font-medium ${theme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>I cluster UMAP verranno generati al termine dell'analisi.</p>
                </div>
              )
            )}
      </div>
    </div>
  );
};

export default ClinicalViewer;