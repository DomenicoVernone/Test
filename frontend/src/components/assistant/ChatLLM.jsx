/**
 * Componente Assistente Clinico (LLM Context-Aware).
 * Interfaccia di chat per interrogare il modello linguistico.
 * Invia il messaggio, l'ID del task e la history della conversazione
 * al backend per abilitare lo Spatial RAG con memoria multi-turno.
 */
import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Bot, User as UserIcon, Loader2 } from 'lucide-react';
import { llmApi } from '../../services/api';


export default function ChatLLM({ isAnalyzing, theme, prediction, taskId }) {
  
  // --- STATO LOCALE ---
  const [inputValue, setInputValue] = useState('');
  const [isLoadingAI, setIsLoadingAI] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'ai',
      text: 'Benvenuto, Dottore. Sono pronto ad assisterla nella valutazione del caso confrontando il profilo del paziente con il database clinico.'
    }
  ]);

  const messagesEndRef = useRef(null);

  // --- EFFETTI ---
  // Scroll automatico verso l'ultimo messaggio
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoadingAI]);

  // Resetta la chat se il medico seleziona un nuovo paziente/task
  useEffect(() => {
    setMessages([
      {
        id: 'welcome',
        sender: 'ai',
        text: 'Benvenuto, Dottore. Sono pronto ad assisterla nella valutazione del caso confrontando il profilo del paziente con il database clinico.'
      }
    ]);
  }, [taskId]);

  // --- HANDLERS ---
  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isAnalyzing || isLoadingAI || !taskId) return;
    
    const userMessageTesto = inputValue.trim();
    
    // 1. Aggiungiamo subito il messaggio del medico alla UI
    const newUserMessage = { id: Date.now().toString(), sender: 'user', text: userMessageTesto };
    setMessages(prev => [...prev, newUserMessage]);
    setInputValue('');
    setIsLoadingAI(true);

    try {
      // 2. Costruiamo la history da inviare al backend.
      // Escludiamo il messaggio di benvenuto (id: 'welcome') e il messaggio
      // appena aggiunto, che viene passato separatamente nel campo 'message'.
      // Il backend inserirà la history tra il system prompt e il messaggio corrente.
      const history = messages
        .filter(m => m.id !== 'welcome')
        .map(m => ({
          role: m.sender === 'user' ? 'user' : 'assistant',
          content: m.text
        }));

      // 3. Chiamata API al backend FastAPI (endpoint /chat/)
      const response = await llmApi.post('/chat/', {
        task_id: taskId,
        message: userMessageTesto,
        history: history
      });

      // 4. Riceviamo la risposta e la aggiungiamo alla UI
      const aiResponseTesto = response.data.response || "Risposta non valida dal server.";
      const newAIMessage = { id: Date.now().toString() + '-ai', sender: 'ai', text: aiResponseTesto };
      setMessages(prev => [...prev, newAIMessage]);

    } catch (error) {
      console.error("Errore durante la comunicazione con l'LLM:", error);
      const errorMessage = { 
        id: Date.now().toString() + '-err', 
        sender: 'ai', 
        text: "Mi scusi Dottore, si è verificato un errore di connessione con il motore AI. Verifichi che il file dei risultati sia disponibile." 
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoadingAI(false);
    }
  };

  // --- CLASSI TAILWIND ---
  const isDark = theme === 'dark';
  const containerClass = isDark ? 'bg-slate-900 text-slate-200' : 'bg-white text-slate-800';
  const headerClass = isDark ? 'border-slate-700 bg-slate-800' : 'border-slate-100 bg-white';
  const badgeClass = isDark ? 'bg-blue-900/40 text-blue-400 border border-blue-800/50' : 'bg-blue-50 text-clinical-primary';
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

      {/* AREA MESSAGGI */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        
        {messages.map((msg) => (
          <div key={msg.id} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-3 max-w-[85%] ${msg.sender === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              
              {/* Avatar Icon */}
              <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${
                msg.sender === 'user' 
                  ? 'bg-blue-100 text-blue-600' 
                  : isDark ? 'bg-slate-800 text-clinical-primary border border-slate-700' : 'bg-white shadow-sm text-clinical-primary border border-slate-100'
              }`}>
                {msg.sender === 'user' ? <UserIcon size={16} /> : <Bot size={16} />}
              </div>

              {/* Bolla del Testo */}
              <div className={`p-3 rounded-xl text-sm leading-relaxed shadow-sm ${
                msg.sender === 'user'
                  ? 'bg-clinical-primary text-white rounded-tr-none'
                  : isDark ? 'bg-slate-800 border border-slate-700 text-slate-300 rounded-tl-none' : 'bg-slate-50 border border-slate-100 text-slate-600 rounded-tl-none'
              }`}>
                {/* Gestione degli a capo nel testo */}
                <p className="whitespace-pre-wrap">{msg.text}</p>
                
                {/* Mostra la predizione solo nel bollo di benvenuto, se presente */}
                {msg.id === 'welcome' && prediction && (
                  <div className={`mt-3 p-2 rounded-lg text-xs font-semibold flex items-center justify-between border ${isDark ? 'bg-slate-900/50 border-slate-700' : 'bg-white border-slate-200 text-slate-700'}`}>
                    <span>Esito Analisi Rilevato:</span>
                    <span className="text-clinical-primary uppercase">{prediction}</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {/* Indicatore di Caricamento AI */}
        {isLoadingAI && (
          <div className="flex justify-start">
             <div className="flex gap-3 max-w-[85%]">
                <div className={`shrink-0 w-8 h-8 rounded-full flex items-center justify-center mt-1 ${isDark ? 'bg-slate-800 text-clinical-primary border border-slate-700' : 'bg-white shadow-sm text-clinical-primary border border-slate-100'}`}>
                  <Bot size={16} />
                </div>
                <div className={`p-3 rounded-xl flex items-center gap-2 rounded-tl-none ${isDark ? 'bg-slate-800 border border-slate-700' : 'bg-slate-50 border border-slate-100'}`}>
                  <Loader2 className="w-4 h-4 text-clinical-primary animate-spin" />
                  <span className="text-xs text-slate-400 font-medium">L'Assistente sta analizzando lo spazio latente...</span>
                </div>
             </div>
          </div>
        )}

        {/* Ancora invisibile per forzare lo scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* AREA INPUT FORM */}
      <form onSubmit={handleSendMessage} className={`p-4 border-t transition-colors ${footerClass}`}>
        {/* Avviso se manca il task_id */}
        {!taskId && !isAnalyzing && (
           <div className="text-xs text-amber-600 bg-amber-50 p-2 mb-2 rounded border border-amber-200 text-center">
             Seleziona un paziente dalla cronologia per abilitare l'assistente.
           </div>
        )}

        <div className="relative">
          <input 
            type="text" 
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={taskId ? "Chiedi un'interpretazione..." : "In attesa di dati clinici..."}
            disabled={isAnalyzing || isLoadingAI || !taskId}
            className={`w-full p-3 pr-12 text-sm rounded-xl border focus:outline-none focus:ring-2 focus:border-transparent transition-colors ${inputClass} ${isAnalyzing || isLoadingAI || !taskId ? 'opacity-50 cursor-not-allowed' : ''}`}
          />
          <button 
            type="submit"
            disabled={isAnalyzing || isLoadingAI || !inputValue.trim() || !taskId}
            className={`absolute right-2 top-2 p-1.5 rounded-lg transition-all ${
              isAnalyzing || isLoadingAI || !inputValue.trim() || !taskId
                ? 'bg-slate-300 text-slate-100 cursor-not-allowed' 
                : 'bg-clinical-primary text-white hover:bg-blue-600 shadow-sm active:scale-95'
            }`}
          >
            {isLoadingAI ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
          </button>
        </div>
        <p className={`text-center text-[9px] mt-2 italic ${isDark ? 'text-slate-500' : 'text-slate-400'}`}>
          Supporto Diagnostico Digitale. Verificare sempre i dati grezzi NIfTI.
        </p>
      </form>

    </div>
  );
}