/**
 * Componente per il caricamento dei file (NIfTI/DICOM).
 * Gestisce visivamente gli stati di idle, caricamento in corso, successo o errore.
 *
 * @param {Object} props
 * @param {File|null} props.file - Il file correntemente selezionato.
 * @param {string} props.uploadStatus - Stato del caricamento ('idle', 'uploading', 'success', 'error').
 * @param {Function} props.onFileChange - Handler scatenato alla selezione di un file.
 * @param {Function} props.onUpload - Handler per inviare il file al backend.
 * @param {string} props.theme - Tema grafico attuale ('light' o 'dark').
 */
import React, { useRef } from 'react';
import { FileUp, CheckCircle2, AlertCircle } from 'lucide-react';

const UploadZone = ({ file, uploadStatus, onFileChange, onUpload, theme }) => {
  const fileInputRef = useRef(null);
  const isDark = theme === 'dark';

  // --- CLEAN CODE: Gestione Temi e Stati ---
  const getBorderColor = () => {
    if (uploadStatus === 'success') {
      return isDark ? 'border-emerald-500 bg-emerald-900/20' : 'border-clinical-success bg-emerald-50';
    }
    if (uploadStatus === 'error') {
      return isDark ? 'border-red-500 bg-red-900/20' : 'border-clinical-danger bg-red-50';
    }
    return isDark 
      ? 'border-slate-700 hover:border-blue-500 hover:bg-slate-800/60' 
      : 'border-clinical-border hover:border-clinical-primary hover:bg-blue-50/50';
  };

  return (
    <div 
      onClick={() => fileInputRef.current?.click()}
      className={`relative overflow-hidden border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all duration-300 cursor-pointer group shadow-clinical-sm ${getBorderColor()} ${isDark ? 'bg-slate-900' : 'bg-clinical-surface'}`}
    >
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={onFileChange} 
        className="hidden" 
        accept=".nii,.nii.gz,.dcm" 
        aria-label="Carica file NIfTI"
      />
      
      {/* Icona Dinamica */}
      {uploadStatus === 'success' ? (
        <CheckCircle2 className={`w-12 h-12 ${isDark ? 'text-emerald-400' : 'text-clinical-success'}`} /> 
      ) : uploadStatus === 'error' ? (
        <AlertCircle className={`w-12 h-12 ${isDark ? 'text-red-400' : 'text-clinical-danger'}`} /> 
      ) : (
        <div className={`p-4 rounded-full transition-colors duration-300 ${isDark ? 'bg-slate-800 group-hover:bg-slate-700' : 'bg-clinical-bg group-hover:bg-blue-100'}`}>
          <FileUp className={`w-8 h-8 ${file ? 'text-clinical-primary' : (isDark ? 'text-slate-500 group-hover:text-blue-400' : 'text-slate-300 group-hover:text-clinical-primary')}`} />
        </div>
      )}

      {/* Testo Descrittivo */}
      <div className="text-center">
        <p className={`text-lg font-bold transition-colors duration-300 ${isDark ? 'text-white' : 'text-slate-800'}`}>
          {file ? file.name : "Carica Esame MRI"}
        </p>
        <p className={`text-sm font-medium transition-colors duration-300 ${isDark ? 'text-slate-400' : 'text-clinical-secondary'}`}>
          {file ? `${(file.size / (1024*1024)).toFixed(2)} MB` : "Seleziona file NIfTI (.nii) o DICOM"}
        </p>
      </div>

      {/* Bottone di Conferma */}
      {file && uploadStatus !== 'success' && (
        <button 
          onClick={(e) => { e.stopPropagation(); onUpload(); }}
          disabled={uploadStatus === 'uploading'}
          className={`mt-2 px-8 py-2 text-white rounded-lg font-bold text-sm shadow-clinical-md transition-all active:scale-95 ${
            uploadStatus === 'uploading' ? 'bg-blue-400 cursor-not-allowed' : 'bg-clinical-primary hover:bg-blue-600'
          }`}
        >
          {uploadStatus === 'uploading' ? "Trasferimento..." : "Conferma Invio"}
        </button>
      )}
    </div>
  );
};

export default UploadZone;