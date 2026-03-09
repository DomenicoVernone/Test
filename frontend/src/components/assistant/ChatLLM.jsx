// File: frontend/src/components/assistant/ChatLLM.jsx
/**
 * Componente Assistente Clinico (LLM).
 * Fornisce un'interfaccia di chat per interrogare un modello linguistico 
 * riguardo l'interpretazione della predizione o dello storico clinico.
 * Attualmente configurato come scheletro architetturale ("Dumb Component" con stato locale isolato).
 *
 * @param {Object} props
 * @param {boolean} props.isAnalyzing - Disabilita la chat se l'Orchestratore backend sta lavorando.
 * @param {string} props.theme - Tema grafico attuale ('light' o 'dark').
 * @param {string|null} props.prediction - Diagnosi restituita dal motore di Inferenza R.
 */
import React, { useState } from 'react';
import { Send, MessageSquare } from 'lucide-react';

export default function ChatLLM({ isAnalyzing, theme, prediction }) {
  
  // --- STATO LOCALE ---
  // Rende l'input un Controlled Component, pronto per essere inviato all'API
  const [inputValue, setInputValue] = useState('');

  // --- HANDLERS ---
  const handleSendMessage = (e) => {
    e.preventDefault(); // Previene il ricaricamento della pagina al submit
    if (!inputValue.trim() || isAnalyzing) return;
    
    // TODO (Futuro): Qui inietteremo la chiamata ad api.post('/llm/chat')
    console.log("🚀 [LLM Stub] Richiesta pronta per l'invio:", inputValue);
    setInputValue(''); // Svuota il campo dopo l'invio
  };

  // --- CLASSI TAILWIND SEMANTICHE (Clean Code) ---
  const isDark = theme === 'dark';
  const containerClass = isDark ? 'bg-slate-900 text-slate-200' : 'bg-white text-slate-800';
  const headerClass = isDark ? 'border-slate-700 bg-slate-800' : 'border-slate-100 bg-white';
  const badgeClass = isDark ? 'bg-blue-900/40 text-blue-400 border border-blue-800/50' : 'bg-blue-50 text-clinical-primary';
  const bubbleClass = isDark ? 'bg-slate-800 border border-slate-700 text-slate-300' : 'bg-slate-50 border border-slate-100 text-slate-600';
  const footerClass = isDark ? 'border-slate-700 bg-slate-800/50' : 'border-slate-100 bg-white';
  const inputClass = isDark ? 'bg-slate-900 border-slate-600 text-white placeholder-slate-500 focus:ring-blue-500' : 'bg-slate-50 border-slate-200 text-slate-800 placeholder-slate-400 focus:ring-clinical-primary';

  return (
    <div className={`flex flex-col h-full transition-colors duration-300 ${containerClass}`}>
      
      {/* HEADER CHAT */}
      <div className={`p-4 border-b flex items-center justify-between transition-colors ${headerClass}`}>
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-clinical-primary" />
          <h3 className="font-bold text-sm">Clinical Assistant</h3>
        </div>
        <span className={`text-[10px] font-bold px-2 py-1 rounded-md uppercase tracking-wider ${badgeClass}`}>
          AI Support
        </span>
      </div>

      {/* AREA MESSAGGI (Viewport) */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        
        {/* Bolla di Benvenuto Sistema */}
        <div className={`p-4 rounded-xl text-sm leading-relaxed shadow-sm transition-colors ${bubbleClass}`}>
          <p>Benvenuto, Dottore. Sono pronto ad assisterla nella valutazione del caso confrontando il profilo del paziente con il database clinico.</p>
          
          {/* Mostriamo il contesto clinico attuale al medico */}
          {prediction && (
            <div className={`mt-3 p-2 rounded-lg text-xs font-semibold flex items-center justify-between border ${isDark ? 'bg-slate-900/50 border-slate-700' : 'bg-white border-slate-200'}`}>
              <span>Esito Analisi Rilevato:</span>
              <span className="text-clinical-primary">{prediction}</span>
            </div>
          )}
        </div>

        {/* TODO (Futuro): Mappare qui i messaggi della cronologia.
          Es: messages.map(msg => <MessageBubble key={msg.id} data={msg} />) 
        */}

      </div>

      {/* AREA INPUT (Ora è un form HTML valido) */}
      <form onSubmit={handleSendMessage} className={`p-4 border-t transition-colors ${footerClass}`}>
        <div className="relative">
          <input 
            type="text" 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Chiedi un'interpretazione o una spiegazione..." 
            disabled={isAnalyzing}
            aria-label="Messaggio per l'assistente AI"
            className={`w-full p-3 pr-12 text-sm rounded-xl border focus:outline-none focus:ring-2 focus:border-transparent transition-colors ${inputClass} ${isAnalyzing ? 'opacity-50 cursor-not-allowed' : ''}`}
          />
          <button 
            type="submit"
            disabled={isAnalyzing || !inputValue.trim()}
            aria-label="Invia messaggio"
            className={`absolute right-2 top-2 p-1.5 rounded-lg transition-all ${
              isAnalyzing || !inputValue.trim()
                ? 'bg-slate-300 text-slate-100 cursor-not-allowed' 
                : 'bg-clinical-primary text-white hover:bg-blue-600 shadow-sm active:scale-95'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
        <p className={`text-center text-[9px] mt-2 italic ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
          Supporto Diagnostico Digitale. Verificare sempre i dati grezzi NIfTI.
        </p>
      </form>

    </div>
  );
}