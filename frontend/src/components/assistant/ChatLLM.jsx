import { MessageSquare, Brain, Send } from 'lucide-react';

const ChatLLM = ({ isAnalyzing, experiment }) => (
  <section className="col-span-4 bg-clinical-surface flex flex-col overflow-hidden border-l border-clinical-border">
    <div className="p-6 border-b border-clinical-border bg-slate-50/20 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <MessageSquare className="w-5 h-5 text-clinical-primary" />
        <h2 className="font-bold text-slate-800 tracking-tight">Clinical Assistant</h2>
      </div>
      <span className="text-[9px] bg-clinical-primary/10 text-clinical-primary px-2 py-1 rounded font-bold uppercase tracking-widest border border-blue-100">AI Support</span>
    </div>

    <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
      <div className="bg-clinical-bg p-5 rounded-2xl rounded-tl-none border border-clinical-border shadow-clinical-sm">
        <p className="text-sm leading-relaxed text-slate-700">
          Benvenuto, Dottore. Sono pronto ad assisterla nella valutazione del caso confrontando il profilo del paziente con il database <span className="font-bold">{experiment}</span>.
        </p>
      </div>
      {isAnalyzing && (
        <div className="flex items-center gap-2 text-clinical-primary italic text-[11px] animate-pulse font-medium">
          <Brain className="w-4 h-4" /> Elaborazione insight diagnostici...
        </div>
      )}
    </div>

    <div className="p-6 border-t border-clinical-border bg-slate-50/10">
      <div className="relative group">
        <input 
          type="text" placeholder="Chiedi un'interpretazione..."
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
);

export default ChatLLM;