import React from 'react';
import { Brain, LineChart, Activity } from 'lucide-react';
import NiiVueCanvas from './NiiVue';
import UmapPlot from './UmapPlot';

const ClinicalViewer = ({ file, niftiUrl, activeTab, setActiveTab, isAnalyzing, umapData, selectedModel }) => {
  
  return (
    <div className="flex-1 bg-white rounded-2xl border border-slate-200 flex flex-col overflow-hidden shadow-sm">
      
      {/* BARRA SUPERIORE */}
      <div className="flex border-b border-slate-200 bg-slate-50 p-1 z-10">
        <button 
          onClick={() => setActiveTab('3d')}
          className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeTab === '3d' ? 'bg-white text-clinical-primary shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}
        >
          <Brain className="w-4 h-4" /> RICOSTRUZIONE ANATOMICA
        </button>
        <button 
          onClick={() => setActiveTab('umap')}
          className={`flex-1 px-4 py-3 text-xs font-bold flex items-center justify-center gap-2 rounded-xl transition-all ${activeTab === 'umap' ? 'bg-white text-clinical-primary shadow-sm border border-slate-200' : 'text-slate-500 hover:text-slate-700'}`}
        >
          <LineChart className="w-4 h-4" /> SPAZIO LATENTE (UMAP)
        </button>
      </div>

      <div className="flex-1 flex flex-col relative bg-slate-50/30 overflow-hidden">
        
        {isAnalyzing ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-4 text-center z-10 bg-white/80 backdrop-blur-sm">
            <div className="h-10 w-10 border-4 border-clinical-primary/20 border-t-clinical-primary rounded-full animate-spin"></div>
            <div>
              <p className="text-[10px] font-bold text-clinical-secondary uppercase tracking-[0.3em]">Elaborazione in corso</p>
              <p className="text-[9px] text-slate-400 italic">Segmentazione volumetrica e proiezione spazio latente...</p>
            </div>
          </div>
        ) : 
        
        activeTab === '3d' ? (
          (file || niftiUrl) ? (
            <NiiVueCanvas file={file} niftiUrl={niftiUrl} />
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center p-10 z-10 text-center">
              <Activity className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p className="text-slate-500 italic text-sm font-medium">In attesa del segnale anatomico NIfTI...</p>
            </div>
          )
        ) : 
        
        (
          /* LAYOUT UMAP: MASSIMIZZATO AL 100% DELLO SPAZIO DISPONIBILE */
          umapData ? (
             <div className="flex-1 w-full h-full relative bg-white p-2">
                 <UmapPlot data={umapData} selectedModel={selectedModel} />
             </div>
          ) : (
            <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
              <Activity className="w-12 h-12 mx-auto mb-4 text-slate-300" />
              <p className="italic text-sm font-medium">I cluster UMAP verranno generati al termine dell'analisi.</p>
            </div>
          )
        )}
      </div>
    </div>
  );
};

export default ClinicalViewer;