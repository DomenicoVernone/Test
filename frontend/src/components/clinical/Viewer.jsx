import React from 'react';
import { Brain, LineChart, Activity } from 'lucide-react';
import NiiVueCanvas from './NiiVue';

const ClinicalViewer = ({ file, activeTab, setActiveTab, isAnalyzing }) => {
  return (
    <div className="flex-1 bg-clinical-surface rounded-2xl border border-clinical-border flex flex-col overflow-hidden shadow-clinical-sm">
      
      <div className="flex border-b border-clinical-border bg-slate-50/50 p-1 z-10">
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

      <div className="flex-1 flex items-center justify-center relative bg-slate-100/20 overflow-hidden">
        
        {isAnalyzing ? (
          <div className="flex flex-col items-center gap-4 text-center z-10">
            <div className="h-10 w-10 border-4 border-clinical-primary/20 border-t-clinical-primary rounded-full animate-spin"></div>
            <div>
              <p className="text-[10px] font-bold text-clinical-secondary uppercase tracking-[0.3em]">Elaborazione in corso</p>
              <p className="text-[9px] text-slate-400 italic">Segmentazione volumetrica e proiezione spazio latente...</p>
            </div>
          </div>
        ) : 
        
        activeTab === '3d' ? (
          file ? (
            <NiiVueCanvas file={file} />
          ) : (
            <div className="text-center p-10 z-10">
              <Activity className="w-12 h-12 mx-auto mb-4 text-slate-200" />
              <p className="text-clinical-secondary italic text-sm font-medium">
                In attesa del segnale anatomico NIfTI...
              </p>
            </div>
          )
        ) : 
        
        (
          <div className="text-center p-10 z-10">
            <Activity className="w-12 h-12 mx-auto mb-4 text-slate-200" />
            <p className="text-clinical-secondary italic text-sm font-medium">
              I cluster UMAP verranno generati al termine dell'analisi.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClinicalViewer;