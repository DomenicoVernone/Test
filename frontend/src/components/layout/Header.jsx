/**
 * Componente Intestazione Principale.
 * Mostra il branding, lo stato della connessione (online/offline) e
 * gestisce il menu utente (Logout) leggendo il payload del JWT.
 */
import React, { useState, useRef, useEffect, useMemo } from 'react';
import { Activity, User, Settings, LogOut } from 'lucide-react';
import { jwtDecode } from 'jwt-decode';

import { useAuth } from '../../contexts/AuthContext';

const Header = ({ onOpenSettings, theme }) => { 
  
  const { logout, token } = useAuth();
  
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isOnline, setIsOnline] = useState(navigator.onLine); 
  const dropdownRef = useRef(null);
  const isDark = theme === 'dark';

  // --- PERFORMANCE OPTIMIZATION (useMemo) ---
  // Decodifica il token solo quando cambia, non ad ogni renderizzazione del componente!
  const username = useMemo(() => {
    if (!token) return "Medico";
    try {
      const decoded = jwtDecode(token);
      return decoded.sub || "Medico";
    } catch (error) {
      console.error("Errore decodifica JWT:", error);
      return "Medico";
    }
  }, [token]);

  // --- GESTIONE EVENTI ESTERNI ---
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
    <header className={`relative z-40 h-16 flex items-center justify-between px-6 shadow-sm transition-colors duration-300 ${isDark ? 'bg-slate-900 border-b border-slate-800' : 'bg-white border-b border-slate-200'}`}>
      
      {/* BRANDING */}
      <div className="flex items-center gap-3">
        <div className="bg-blue-600 p-2 rounded-lg shadow-sm">
          <Activity className="text-white w-5 h-5" />
        </div>
        <h1 className={`text-xl font-bold tracking-tight uppercase italic ${isDark ? 'text-white' : 'text-slate-800'}`}>
          Clinical<span className="text-blue-600 font-black">Twin</span>
        </h1>
      </div>

      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4">
          
          {/* MENU UTENTE DROPDOWN */}
          <div className="relative" ref={dropdownRef}>
            <button 
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              aria-label="Menu Utente"
              className={`w-9 h-9 rounded-full border flex items-center justify-center transition-colors cursor-pointer ${
                isDropdownOpen 
                  ? 'border-blue-500 text-blue-500 bg-blue-50/10' 
                  : (isDark ? 'border-slate-700 text-slate-400 hover:bg-slate-800' : 'border-slate-300 text-slate-500 hover:bg-slate-100')
              }`}
            >
              <User className="w-5 h-5" />
            </button>

            {isDropdownOpen && (
              <div className={`absolute right-0 mt-3 w-64 rounded-xl shadow-xl border py-1 origin-top-right transition-all animate-in fade-in zoom-in duration-150 ${isDark ? 'bg-slate-800 border-slate-700' : 'bg-white border-slate-200'}`}>
                <div className={`px-5 py-4 border-b rounded-t-xl ${isDark ? 'border-slate-700 bg-slate-900/50' : 'border-slate-100 bg-slate-50/50'}`}>
                  <p className={`text-base font-bold truncate ${isDark ? 'text-white' : 'text-slate-800'}`}>{username}</p>
                  <div className="flex items-center gap-2 mt-1.5">
                    <div className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
                    <p className={`text-[11px] font-bold uppercase tracking-wider ${isOnline ? 'text-green-500' : 'text-red-500'}`}>
                      {isOnline ? 'Sistema Online' : 'Offline - Rete Assente'}
                    </p>
                  </div>
                </div>
                
                <button onClick={logout} className={`w-full text-left px-5 py-3.5 text-sm flex items-center gap-3 font-semibold transition-colors rounded-b-xl mt-1 ${isDark ? 'text-red-400 hover:bg-slate-700/50' : 'text-red-600 hover:bg-red-50'}`}>
                  <LogOut className="w-4.5 h-4.5" />
                  <span>Disconnetti</span>
                </button>
              </div>
            )}
          </div>

          {/* PULSANTE IMPOSTAZIONI */}
          <button 
            onClick={onOpenSettings}
            aria-label="Impostazioni"
            className={`p-2 -mr-2 rounded-full transition-colors ${isDark ? 'text-slate-400 hover:text-blue-400 hover:bg-slate-800' : 'text-slate-400 hover:text-blue-600 hover:bg-slate-100'}`}
          >
            <Settings className="w-5 h-5" />
          </button>
          
        </div>
      </div>
    </header>
  );
};

export default Header;