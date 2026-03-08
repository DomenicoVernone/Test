import React from 'react';
import { X, Palette, Moon } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, colorMap, setColorMap, theme, setTheme }) {
  if (!isOpen) return null;

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
      <div className="bg-white p-8 rounded-2xl shadow-2xl w-112.5 flex flex-col gap-6 animate-in fade-in zoom-in duration-200">
        
        {/* Intestazione */}
        <div className="flex justify-between items-start">
          <div>
            <h3 className="text-2xl font-bold text-slate-800">Impostazioni</h3>
            <p className="text-sm text-slate-500 mt-1">Personalizza l'ambiente clinico</p>
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-full transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Corpo Impostazioni */}
        <div className="flex flex-col gap-6 py-2">
          
          {/* SEZIONE 1: Color Map Risonanza */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 text-slate-700 font-bold text-sm uppercase tracking-wide border-b border-slate-100 pb-2">
              <Palette className="w-4 h-4 text-clinical-primary" />
              Mappa Colori NIfTI
            </div>
            <select 
              value={colorMap}
              onChange={(e) => setColorMap(e.target.value)}
              className="w-full p-3 border border-slate-200 rounded-xl bg-slate-50 text-slate-700 font-semibold focus:outline-none focus:border-clinical-primary focus:ring-1 focus:ring-clinical-primary cursor-pointer"
            >
              <option value="gray">Scala di Grigi (Standard)</option>
              <option value="inferno">Inferno (Evidenziazione Atrofie)</option>
              <option value="hot">Hot (Mappa di Calore)</option>
              <option value="winter">Winter (Contrasto Freddo)</option>
            </select>
          </div>

          {/* SEZIONE 2: Tema Interfaccia */}
          <div className="flex flex-col gap-3">
            <div className="flex items-center gap-2 text-slate-700 font-bold text-sm uppercase tracking-wide border-b border-slate-100 pb-2">
              <Moon className="w-4 h-4 text-clinical-primary" />
              Tema Interfaccia
            </div>
            <div className="flex bg-slate-100 p-1 rounded-xl">
              <button 
                onClick={() => setTheme('light')}
                className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${theme === 'light' ? 'bg-white text-clinical-primary shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                Chiaro
              </button>
              <button 
                onClick={() => setTheme('dark')}
                className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${theme === 'dark' ? 'bg-slate-800 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                Scuro
              </button>
            </div>
          </div>

        </div>

        {/* Footer */}
        <div className="flex justify-end mt-2 pt-4 border-t border-slate-100">
          <button onClick={onClose} className="px-6 py-3 bg-clinical-primary text-white rounded-xl font-bold hover:bg-blue-600 shadow-md active:scale-95 transition-all">
            Salva e Chiudi
          </button>
        </div>

      </div>
    </div>
  );
}