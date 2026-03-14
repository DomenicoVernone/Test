/**
 * Componente per il caricamento dei file (NIfTI/DICOM).
 * Gestisce visivamente gli stati di idle, caricamento in corso, successo o errore.
 *
 * @param {Object} props
 * @param {File|null} props.file - Il file correntemente selezionato (anteprima).
 * @param {number} props.filesCount - Numero totale di file selezionati per il batch.
 * @param {string} props.uploadStatus - Stato del caricamento ('idle', 'uploading', 'success', 'error').
 * @param {Function} props.onFileChange - Handler scatenato alla selezione di un file.
 * @param {Function} props.onUpload - Handler per inviare il/i file al backend.
 * @param {string} props.theme - Tema grafico attuale ('light' o 'dark').
 */
import React, { useRef } from 'react';
import { FileUp, Files, CheckCircle2, AlertCircle } from 'lucide-react'; 

const UploadZone = ({ file, files = [], uploadStatus, onFileChange, onFileSelect, onUpload, onClear, theme }) => {
  const fileInputRef = useRef(null);
  const isDark = theme === 'dark';
  const filesCount = files.length; // Calcoliamo dinamicamente il numero

  // --- Gestione Temi e Stati ---
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

  const hasFiles = filesCount > 0 || file;

  return (
    <div
      onClick={() => fileInputRef.current?.click()}
      className={`relative overflow-hidden border-2 border-dashed rounded-2xl p-4 flex flex-col items-center justify-center gap-2 transition-all duration-300 cursor-pointer group shadow-clinical-sm ${getBorderColor()} ${isDark ? 'bg-slate-900' : 'bg-clinical-surface'}`}
    >
      <input
        type="file"
        ref={fileInputRef}
        onChange={onFileChange}
        className="hidden"
        accept=".nii,.nii.gz,.dcm"
        aria-label="Carica file NIFTI"
        multiple // <-- LA MAGIA DEL BATCH UPLOAD
      />

      {/* Icona Dinamica (Leggermente più compatta) */}
      {uploadStatus === 'success' ? (
        <CheckCircle2 className={`w-10 h-10 ${isDark ? 'text-emerald-400' : 'text-clinical-success'}`} />
      ) : uploadStatus === 'error' ? (
        <AlertCircle className={`w-10 h-10 ${isDark ? 'text-red-400' : 'text-clinical-danger'}`} />
      ) : (
        <div className={`p-2 rounded-full transition-colors duration-300 ${isDark ? 'bg-slate-800 group-hover:bg-slate-700' : 'bg-clinical-bg group-hover:bg-blue-100'}`}>
          {/* Se ci sono più file, mostriamo l'icona multipla */}
          {filesCount > 1 ? (
            <Files className="w-7 h-7 text-clinical-primary" />
          ) : (
            <FileUp className={`w-7 h-7 ${hasFiles ? 'text-clinical-primary' : (isDark ? 'text-slate-500 group-hover:text-blue-400' : 'text-slate-300 group-hover:text-clinical-primary')}`} />
          )}
        </div>
      )}

      {/* Testo Descrittivo Dinamico */}
      <div className="text-center">
        <p className={`text-base font-bold transition-colors duration-300 ${isDark ? 'text-white' : 'text-slate-800'}`}>
          {filesCount > 1
            ? `${filesCount} Esami Selezionati`
            : file ? file.name : "Carica Esame MRI"}
        </p>
        <p className={`text-xs font-medium transition-colors duration-300 ${isDark ? 'text-slate-400' : 'text-clinical-secondary'}`}>
          {filesCount > 1
            ? "Pronto per l'analisi multipla in background"
            : file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : "Seleziona uno o più file NIFTI (.nii)"}
        </p>
      </div>

      {/* Mini-Switcher: Staging Area dei file multipli (SCORRIMENTO + CENTRATURA SICURA) */}
      {filesCount > 1 && uploadStatus !== 'success' && (
        <div 
          className="w-full mt-1 overflow-x-auto pb-2 px-2"
          style={{ scrollbarWidth: 'thin' }} 
          onClick={(e) => e.stopPropagation()} 
        >
          {/* w-max mx-auto è la magia: centra se sono pochi, fa scrollare normalmente se sono tanti! */}
          <div className="flex gap-2 w-max mx-auto items-center">
            {files.map((f, index) => (
              <button
                key={index}
                onClick={(e) => {
                  e.stopPropagation(); 
                  if (onFileSelect) onFileSelect(f); 
                }}
                className={`shrink-0 text-[11px] px-3 py-1 rounded-full border transition-all truncate max-w-37.5 shadow-sm ${
                  file?.name === f.name
                    ? (isDark ? 'bg-blue-600 border-blue-400 text-white' : 'bg-clinical-primary border-blue-500 text-white shadow-md')
                    : (isDark ? 'bg-slate-800 border-slate-600 text-slate-300 hover:bg-slate-700' : 'bg-white border-slate-300 text-slate-600 hover:border-clinical-primary')
                }`}
                title={f.name} 
              >
                {f.name}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Pulsanti Azione (Annulla + Conferma) */}
      {hasFiles && uploadStatus !== 'success' && (
        <div className="mt-1 flex gap-3 items-center">
          
          {/* Pulsante Svuota/Annulla */}
          <button
            onClick={(e) => { 
              e.stopPropagation(); 
              if (onClear) onClear(); 
            }}
            disabled={uploadStatus === 'uploading'}
            className={`px-4 py-1.5 rounded-lg font-bold text-xs transition-all ${
              uploadStatus === 'uploading'
                ? 'opacity-50 cursor-not-allowed'
                : isDark ? 'bg-slate-800 hover:bg-slate-700 text-slate-300' : 'bg-slate-200 hover:bg-slate-300 text-slate-700'
            }`}
          >
            Svuota
          </button>

          {/* Pulsante Conferma (Invariato) */}
          <button
            onClick={(e) => { e.stopPropagation(); onUpload(); }}
            disabled={uploadStatus === 'uploading'}
            className={`px-8 py-1.5 text-white rounded-lg font-bold text-sm shadow-clinical-md transition-all active:scale-95 ${
              uploadStatus === 'uploading' 
                ? 'bg-blue-400 cursor-not-allowed' 
                : 'bg-clinical-primary hover:bg-blue-600'
            }`}
          >
            {uploadStatus === 'uploading'
              ? "Trasferimento..."
              : filesCount > 1 ? "Analisi Batch" : "Conferma Invio"}
          </button>
        </div>
      )}
    </div>
  );
};

export default UploadZone;