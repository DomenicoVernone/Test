import React, { useState } from 'react';
import { X, Palette, Moon } from 'lucide-react';

export default function SettingsModal({ isOpen, onClose, colorMap, setColorMap, theme, setTheme }) {
  // 1. STATI LOCALI e tracciamento dell'apertura
  const [localColorMap, setLocalColorMap] = useState(colorMap);
  const [localTheme, setLocalTheme] = useState(theme);
  const [prevIsOpen, setPrevIsOpen] = useState(isOpen);

  // 2. SINCRONIZZAZIONE "RENDER-PHASE" (Addio useEffect!)
  // React controlla questo blocco durante il render. Se la modale si sta aprendo,
  // allinea i dati locali prima ancora di disegnare lo schermo. Zero sprechi di performance!
  if (isOpen !== prevIsOpen) {
    setPrevIsOpen(isOpen);
    if (isOpen) {
      setLocalColorMap(colorMap);
      setLocalTheme(theme);
    }
  }

  if (!isOpen) return null;

  // 3. IL VERO SALVATAGGIO
  const handleSave = () => {
    setColorMap(localColorMap);
    setTheme(localTheme);
    onClose();
  };

  return (
    <div className="absolute inset-0 z-50 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm px-4">
      {/* Usiamo localTheme per mostrare l'anteprima del tema SOLO dentro la modale */}
      <div className={`p-8 rounded-2xl shadow-2xl max-w-md w-full flex flex-col gap-6 animate-in fade-in zoom-in duration-200 transition-colors ${localTheme === 'dark' ? 'bg-slate-800 border border-slate-700' : 'bg-white'}`}>
        
        {/* Intestazione */}
        <div className="flex justify-between items-start">
          <div>
            <h3 className={`text-2xl font-bold ${localTheme === 'dark' ? 'text-white' : 'text-slate-800'}`}>Impostazioni</h3>
            <p className={`text-sm mt-1 ${localTheme === 'dark' ? 'text-slate-400' : 'text-slate-500'}`}>Personalizza l'ambiente clinico</p>
          </div>
          {/* Se clicchi la X, chiama solo onClose, buttando via le modifiche temporanee */}
          <button onClick={onClose} className={`p-2 rounded-full transition-colors ${localTheme === 'dark' ? 'text-slate-400 hover:bg-slate-700 hover:text-white' : 'text-slate-400 hover:bg-slate-100 hover:text-slate-600'}`}>
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex flex-col gap-6 py-2">
          
          {/* Mappa Colori NIfTI */}
          <div className="flex flex-col gap-3">
            <div className={`flex items-center gap-2 font-bold text-sm uppercase tracking-wide border-b pb-2 ${localTheme === 'dark' ? 'text-slate-300 border-slate-700' : 'text-slate-700 border-slate-100'}`}>
              <Palette className="w-4 h-4 text-blue-500" />
              Mappa Colori Risonanza
            </div>
            <select 
              value={localColorMap}
              onChange={(e) => setLocalColorMap(e.target.value)}
              className={`w-full p-3 border rounded-xl font-semibold focus:outline-none cursor-pointer transition-colors ${
                localTheme === 'dark' 
                ? 'bg-slate-900 border-slate-600 text-slate-200 focus:border-blue-500' 
                : 'bg-slate-50 border-slate-200 text-slate-700 focus:border-blue-500'
              }`}
            >
              <option value="gray">Scala di Grigi (Standard)</option>
              <option value="inferno">Inferno (Evidenzia Atrofie)</option>
              <option value="hot">Hot (Mappa di Calore)</option>
              <option value="winter">Winter (Contrasto Freddo)</option>
            </select>
          </div>

          {/* Tema Interfaccia */}
          <div className="flex flex-col gap-3">
            <div className={`flex items-center gap-2 font-bold text-sm uppercase tracking-wide border-b pb-2 ${localTheme === 'dark' ? 'text-slate-300 border-slate-700' : 'text-slate-700 border-slate-100'}`}>
              <Moon className="w-4 h-4 text-blue-500" />
              Tema Interfaccia
            </div>
            <div className={`flex p-1 rounded-xl ${localTheme === 'dark' ? 'bg-slate-900' : 'bg-slate-100'}`}>
              <button 
                onClick={() => setLocalTheme('light')}
                className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${localTheme === 'light' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-300'}`}
              >
                Chiaro
              </button>
              <button 
                onClick={() => setLocalTheme('dark')}
                className={`flex-1 py-2 text-sm font-bold rounded-lg transition-all ${localTheme === 'dark' ? 'bg-slate-700 text-white shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}
              >
                Scuro
              </button>
            </div>
          </div>

        </div>

        {/* Footer: Questo è l'unico bottone che fa il vero salvataggio! */}
        <div className={`flex justify-end mt-2 pt-4 border-t ${localTheme === 'dark' ? 'border-slate-700' : 'border-slate-100'}`}>
          <button onClick={handleSave} className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-500 shadow-md active:scale-95 transition-all">
            Salva e Chiudi
          </button>
        </div>

      </div>
    </div>
  );
}