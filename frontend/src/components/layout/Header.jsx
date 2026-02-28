import { Activity, ChevronDown, User, Settings } from 'lucide-react';

const Header = ({ experiment }) => (
  <header className="h-16 border-b border-clinical-border flex items-center justify-between px-6 bg-clinical-surface shadow-clinical-sm z-10">
    <div className="flex items-center gap-3">
      <div className="bg-clinical-primary p-2 rounded-lg shadow-lg shadow-blue-500/20">
        <Activity className="text-white w-5 h-5" />
      </div>
      <h1 className="text-xl font-bold tracking-tight text-slate-800 uppercase italic">
        Clinical<span className="text-clinical-primary font-black">Twin</span>
      </h1>
    </div>
    <div className="flex items-center gap-6">
      <div className="hidden md:flex flex-col items-end border-r border-clinical-border pr-4">
        <span className="text-[10px] text-clinical-secondary uppercase font-bold tracking-widest text-right">Protocollo Attivo</span>
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          {experiment}
          <ChevronDown className="w-4 h-4 text-clinical-secondary" />
        </div>
      </div>
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-full bg-clinical-bg border border-clinical-border flex items-center justify-center text-clinical-secondary hover:bg-slate-100 transition-colors cursor-pointer">
          <User className="w-5 h-5" />
        </div>
        <Settings className="w-5 h-5 text-clinical-secondary cursor-pointer hover:text-slate-600" />
      </div>
    </div>
  </header>
);

export default Header;