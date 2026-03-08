import React, { useRef } from 'react';
import { FileUp, CheckCircle2, AlertCircle } from 'lucide-react';

const UploadZone = ({ file, uploadStatus, onFileChange, onUpload, theme }) => {
  const fileInputRef = useRef(null);

  // Gestione dinamica dei bordi e degli sfondi in base allo stato E al tema
  const getBorderColor = () => {
    if (uploadStatus === 'success') {
      return theme === 'dark' ? 'border-emerald-500 bg-emerald-900/20' : 'border-clinical-success bg-emerald-50';
    }
    if (uploadStatus === 'error') {
      return theme === 'dark' ? 'border-red-500 bg-red-900/20' : 'border-clinical-danger bg-red-50';
    }
    // Stato di default (Idle/Hover)
    return theme === 'dark' 
      ? 'border-slate-700 hover:border-blue-500 hover:bg-slate-800/60' 
      : 'border-clinical-border hover:border-clinical-primary hover:bg-blue-50/50';
  };

  return (
    <div 
      onClick={() => fileInputRef.current?.click()}
      className={`relative overflow-hidden border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all duration-300 cursor-pointer group shadow-clinical-sm ${getBorderColor()} ${theme === 'dark' ? 'bg-slate-900' : 'bg-clinical-surface'}`}
    >
      <input type="file" ref={fileInputRef} onChange={onFileChange} className="hidden" accept=".nii,.gz,.dcm" />
      
      {uploadStatus === 'success' ? (
        <CheckCircle2 className={`w-12 h-12 ${theme === 'dark' ? 'text-emerald-400' : 'text-clinical-success'}`} /> 
      ) : uploadStatus === 'error' ? (
        <AlertCircle className={`w-12 h-12 ${theme === 'dark' ? 'text-red-400' : 'text-clinical-danger'}`} /> 
      ) : (
        <div className={`p-4 rounded-full transition-colors duration-300 ${theme === 'dark' ? 'bg-slate-800 group-hover:bg-slate-700' : 'bg-clinical-bg group-hover:bg-blue-100'}`}>
          <FileUp className={`w-8 h-8 ${file ? 'text-clinical-primary' : (theme === 'dark' ? 'text-slate-500 group-hover:text-blue-400' : 'text-slate-300 group-hover:text-clinical-primary')}`} />
        </div>
      )}

      <div className="text-center">
        <p className={`text-lg font-bold transition-colors duration-300 ${theme === 'dark' ? 'text-white' : 'text-slate-800'}`}>
          {file ? file.name : "Carica Esame MRI"}
        </p>
        <p className={`text-sm font-medium transition-colors duration-300 ${theme === 'dark' ? 'text-slate-400' : 'text-clinical-secondary'}`}>
          {file ? `${(file.size / (1024*1024)).toFixed(2)} MB` : "Seleziona file NIfTI (.nii) o DICOM"}
        </p>
      </div>

      {file && uploadStatus !== 'success' && (
        <button 
          onClick={(e) => { e.stopPropagation(); onUpload(); }}
          className="mt-2 px-8 py-2 bg-clinical-primary text-white rounded-lg font-bold text-sm hover:opacity-95 shadow-clinical-md transition-all active:scale-95"
        >
          {uploadStatus === 'uploading' ? "Trasferimento..." : "Conferma Invio"}
        </button>
      )}
    </div>
  );
};

export default UploadZone;