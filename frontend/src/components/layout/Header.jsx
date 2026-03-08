import React, { useState, useContext, useRef, useEffect } from 'react';
import { Activity, User, Settings, LogOut } from 'lucide-react';
import { AuthContext } from '../../contexts/AuthContext';
import { jwtDecode } from 'jwt-decode';

const Header = ({ onOpenSettings }) => { // <-- Modificato: riceve la funzione per aprire la modale
  const { logout, token } = useContext(AuthContext);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine); 
  const dropdownRef = useRef(null);

  let username = "Medico";
  if (token) {
    try {
      const decoded = jwtDecode(token);
      username = decoded.sub || "Medico";
    } catch (error) {
      console.error("Errore nella decodifica del token:", error);
    }
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    };

    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    document.addEventListener('mousedown', handleClickOutside);
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return (
    <header className="relative z-50 h-16 border-b border-clinical-border flex items-center justify-between px-6 bg-clinical-surface shadow-clinical-sm top-0">
      
      {/* SEZIONE SINISTRA: Logo */}
      <div className="flex items-center gap-3">
        <div className="bg-clinical-primary p-2 rounded-lg shadow-lg shadow-blue-500/20">
          <Activity className="text-white w-5 h-5" />
        </div>
        <h1 className="text-xl font-bold tracking-tight text-slate-800 uppercase italic">
          Clinical<span className="text-clinical-primary font-black">Twin</span>
        </h1>
      </div>

      {/* SEZIONE DESTRA: Controlli Utente & Impostazioni */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4"> {/* Aumentato il gap per respiro */}
          
          <div className="relative" ref={dropdownRef}>
            <div 
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className={`w-9 h-9 rounded-full bg-clinical-bg border flex items-center justify-center transition-colors cursor-pointer ${
                isDropdownOpen ? 'border-clinical-primary text-clinical-primary shadow-sm' : 'border-clinical-border text-clinical-secondary hover:bg-slate-100'
              }`}
            >
              <User className="w-5 h-5" />
            </div>

            {/* Menu a Tendina */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-3 w-64 bg-white rounded-xl shadow-xl border border-slate-200 py-1 origin-top-right transition-all">
                <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50 rounded-t-xl">
                  <p className="text-base font-bold text-slate-800 truncate">{username}</p>
                  
                  <div className="flex items-center gap-2 mt-1.5">
                    <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <p className={`text-[11px] font-bold uppercase tracking-wider ${isOnline ? 'text-green-600' : 'text-red-600'}`}>
                      {isOnline ? 'Sistema Online' : 'Offline - Rete Assente'}
                    </p>
                  </div>
                </div>
                
                <button 
                  onClick={logout}
                  className="w-full text-left px-5 py-3.5 text-sm text-red-600 hover:bg-red-50 flex items-center gap-3 font-semibold transition-colors rounded-b-xl mt-1"
                >
                  <LogOut className="w-4.5 h-4.5" />
                  <span>Disconnetti</span>
                </button>
              </div>
            )}
          </div>

          {/* PULSANTE IMPOSTAZIONI: Ora collegato alla funzione */}
          <button 
            onClick={onOpenSettings}
            className="p-2 -mr-2 text-clinical-secondary hover:text-clinical-primary hover:bg-slate-100 rounded-full transition-colors"
            title="Impostazioni Visualizzatore"
          >
            <Settings className="w-5 h-5" />
          </button>
          
        </div>
      </div>
    </header>
  );
};

export default Header;