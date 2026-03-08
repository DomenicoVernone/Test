import React from 'react';
import { Send, MessageSquare } from 'lucide-react';

export default function ChatLLM({ isAnalyzing, theme, prediction }) {
  
  return (
    <div className={`flex flex-col h-full transition-colors duration-300 ${theme === 'dark' ? 'bg-slate-900 text-slate-200' : 'bg-white text-slate-800'}`}>
      
      {/* HEADER CHAT */}
      <div className={`p-4 border-b flex items-center justify-between transition-colors ${theme === 'dark' ? 'border-slate-700 bg-slate-800' : 'border-slate-100 bg-white'}`}>
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-clinical-primary" />
          <h3 className={`font-bold text-sm ${theme === 'dark' ? 'text-white' : 'text-slate-800'}`}>Clinical Assistant</h3>
        </div>
        <span className={`text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wider ${theme === 'dark' ? 'bg-blue-900/40 text-blue-400 border border-blue-800/50' : 'bg-blue-50 text-clinical-primary'}`}>
          AI Support
        </span>
      </div>

      {/* AREA MESSAGGI */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        
        {/* Bolla di Benvenuto dell'AI */}
        <div className={`p-4 rounded-xl text-sm leading-relaxed shadow-sm transition-colors ${theme === 'dark' ? 'bg-slate-800 border border-slate-700 text-slate-300' : 'bg-slate-50 border border-slate-100 text-slate-600'}`}>
          <p>Benvenuto, Dottore. Sono pronto ad assisterla nella valutazione del caso confrontando il profilo del paziente con il database clinico.</p>
          
          {/* Mostriamo la predizione se è disponibile! */}
          {prediction && (
            <div className={`mt-3 p-2 rounded-lg text-xs font-semibold flex items-center justify-between border ${theme === 'dark' ? 'bg-slate-900/50 border-slate-700' : 'bg-white border-slate-200'}`}>
              <span>Esito Rilevato:</span>
              <span className="text-clinical-primary">{prediction}</span>
            </div>
          )}
        </div>

        {/* Qui in futuro andrà la logica del mapping dei messaggi veri... */}

      </div>

      {/* AREA INPUT */}
      <div className={`p-4 border-t transition-colors ${theme === 'dark' ? 'border-slate-700 bg-slate-800/50' : 'border-slate-100 bg-white'}`}>
        <div className="relative">
          <input 
            type="text" 
            placeholder="Chiedi un'interpretazione o una spiegazione..." 
            disabled={isAnalyzing}
            className={`w-full p-3 pr-12 text-sm rounded-xl border focus:outline-none focus:ring-2 focus:ring-clinical-primary focus:border-transparent transition-colors ${
              theme === 'dark' 
                ? 'bg-slate-900 border-slate-600 text-white placeholder-slate-500' 
                : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400'
            } ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
          />
          <button 
            disabled={isAnalyzing}
            className={`absolute right-2 top-2 p-1.5 rounded-lg transition-all ${
              isAnalyzing 
                ? 'bg-slate-300 text-slate-100 cursor-not-allowed' 
                : 'bg-clinical-primary text-white hover:bg-blue-600 shadow-sm active:scale-95'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className={`text-center text-[9px] mt-2 italic ${theme === 'dark' ? 'text-slate-500' : 'text-slate-400'}`}>
          Supporto Diagnostico Digitale. Verificare sempre i dati grezzi NIfTI.
        </p>
      </div>

    </div>
  );
}