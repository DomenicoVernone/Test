import React, { useRef } from 'react';
import { FileUp, CheckCircle2, AlertCircle } from 'lucide-react';

const UploadZone = ({ file, uploadStatus, onFileChange, onUpload }) => {
  const fileInputRef = useRef(null);

  const getBorderColor = () => {
    if (uploadStatus === 'success') return 'border-clinical-success bg-emerald-50';
    if (uploadStatus === 'error') return 'border-clinical-danger bg-red-50';
    return 'border-clinical-border hover:border-clinical-primary hover:bg-blue-50/50';
  };

  return (
    <div 
      onClick={() => fileInputRef.current?.click()}
      className={`relative overflow-hidden bg-clinical-surface border-2 border-dashed rounded-2xl p-8 flex flex-col items-center justify-center gap-3 transition-all cursor-pointer group shadow-clinical-sm ${getBorderColor()}`}
    >
      <input type="file" ref={fileInputRef} onChange={onFileChange} className="hidden" accept=".nii,.gz,.dcm" />
      
      {uploadStatus === 'success' ? <CheckCircle2 className="w-12 h-12 text-clinical-success" /> : 
       uploadStatus === 'error' ? <AlertCircle className="w-12 h-12 text-clinical-danger" /> : 
       (
        <div className="bg-clinical-bg p-4 rounded-full group-hover:bg-blue-100">
          <FileUp className={`w-8 h-8 ${file ? 'text-clinical-primary' : 'text-slate-300 group-hover:text-clinical-primary'}`} />
        </div>
      )}

      <div className="text-center">
        <p className="text-lg font-bold text-slate-800">{file ? file.name : "Carica Esame MRI"}</p>
        <p className="text-sm text-clinical-secondary font-medium">
          {file ? `${(file.size / (1024*1024)).toFixed(2)} MB` : "Seleziona file NIfTI (.nii) o DICOM"}
        </p>
      </div>

      {file && uploadStatus !== 'success' && (
        <button 
          onClick={(e) => { e.stopPropagation(); onUpload(); }}
          className="mt-2 px-8 py-2 bg-clinical-primary text-white rounded-lg font-bold text-sm hover:opacity-95 shadow-clinical-md"
        >
          {uploadStatus === 'uploading' ? "Trasferimento..." : "Conferma Invio"}
        </button>
      )}
    </div>
  );
};

export default UploadZone;