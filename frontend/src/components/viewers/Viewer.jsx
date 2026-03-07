import React, { useState } from 'react'; // <-- Rimuovi useEffect dall'import
import { Brain, LineChart, Activity } from 'lucide-react';
import NiiVueCanvas from './NiiVue';
import UmapPlot from './UmapPlot';

const ClinicalViewer = ({ file, niftiUrl, activeTab, setActiveTab, isAnalyzing, umapData, prediction, selectedModel }) => {
  
  // 1. Inizializziamo lo stato locale per le Tab
  const [umapModelTab, setUmapModelTab] = useState(selectedModel ? selectedModel.replace('HC_vs_', '') : 'bvFTD');
  
  // 2. Teniamo traccia della prop precedente
  const [prevSelectedModel, setPrevSelectedModel] = useState(selectedModel);

  // 3. REACT 18 PATTERN: Sincronizzazione sincrona senza useEffect
  // Se il modello selezionato dal genitore (Dashboard) è cambiato, aggiorniamo subito lo stato locale
  if (selectedModel !== prevSelectedModel) {
    setPrevSelectedModel(selectedModel);
    setUmapModelTab(selectedModel ? selectedModel.replace('HC_vs_', '') : 'bvFTD');
  }

  const getModelFullName = (tab) => {
    if (tab === 'bvFTD') return 'Variante Comportamentale (bvFTD)';
    if (tab === 'svPPA') return 'Variante Semantica (svPPA)';
    if (tab === 'nfvPPA') return 'Variante Non Fluente (nfvPPA)';
    return '';
  };

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
          /* PASSIAMO SIA IL FILE LOCALE CHE L'URL A NIIVUE */
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
          /* LAYOUT UMAP PULITO E PROFESSIONALE */
          <div className="flex flex-col h-full w-full bg-white">
            
            {/* TABS (Radar Locale) */}
            <div className="flex border-b border-slate-200 bg-slate-100 pt-2 px-2 gap-1">
              {['bvFTD', 'svPPA', 'nfvPPA'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setUmapModelTab(tab)}
                  className={`px-6 py-2 text-sm font-semibold rounded-t-lg border-t border-l border-r transition-all ${
                    umapModelTab === tab ? 'bg-white text-slate-800 border-slate-200 shadow-[0_2px_0_0_white]' : 'bg-slate-200 text-slate-400 border-transparent hover:bg-slate-300'
                  }`}
                >
                  {umapModelTab === tab ? '✓ ' : '× '} VISTA {tab}
                </button>
              ))}
            </div>

            {/* TITOLO CENTRALE */}
            <div className="pt-6 pb-2 text-center bg-white">
              <h2 className="text-lg font-black text-slate-800 tracking-tight">
                VISUALIZZAZIONE SPAZIO LATENTE 3D (UMAP): MODELLO {umapModelTab}
              </h2>
              <p className="text-sm font-mono text-slate-500 mt-1">HC_vs_{umapModelTab}</p>
            </div>

            {/* AREA PRINCIPALE (Grafico + Explainable AI) */}
            <div className="flex-1 flex flex-row overflow-hidden bg-white">
              
              <div className="flex-1 relative p-4">
                {/* Se abbiamo i dati e corrispondono alla tab selezionata, mostra il grafico */}
                {(umapData && selectedModel === `HC_vs_${umapModelTab}`) ? (
                  <UmapPlot data={umapData} />
                ) : (
                  <div className="absolute inset-0 flex flex-col items-center justify-center text-slate-400">
                    <p className="italic">Nessun dato caricato per questa vista.</p>
                  </div>
                )}
              </div>

              {/* Explainable AI Panel (Pulito, senza banner rossi) */}
              <div className="w-72 bg-slate-50 border-l border-slate-200 p-6 flex flex-col gap-6">
                <div>
                  <p className="text-xs text-slate-500 font-bold mb-1 uppercase tracking-wider">Diagnosi Modello:</p>
                  {(prediction && selectedModel === `HC_vs_${umapModelTab}`) ? (
                    <p className="font-bold text-slate-800 text-base">
                      {prediction === 'Malato' ? umapModelTab : 'Sano (Controllo)'}
                    </p>
                  ) : (
                    <p className="text-slate-400 italic text-sm">-</p>
                  )}
                </div>

                <div>
                  <p className="text-xs text-slate-500 font-bold mb-1 uppercase tracking-wider">Conferma Visiva:</p>
                  <p className="text-sm text-slate-700 leading-relaxed">
                    {(prediction && selectedModel === `HC_vs_${umapModelTab}`) 
                      ? `Il paziente si posiziona nel cluster della ${prediction === 'Malato' ? getModelFullName(umapModelTab) : 'coorte sana di controllo'}.` 
                      : '-'}
                  </p>
                </div>
              </div>

            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClinicalViewer;