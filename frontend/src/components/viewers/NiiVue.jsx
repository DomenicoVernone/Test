import React, { useEffect, useRef, useContext } from 'react';
import { Niivue } from '@niivue/niivue';
import { AuthContext } from '../../contexts/AuthContext'; 

const NiiVueCanvas = ({ file, niftiUrl, colorMap = 'gray' }) => {
  const canvasRef = useRef(null);
  const nvRef = useRef(null);
  const { token } = useContext(AuthContext); 

  useEffect(() => {
    // Inizializzazione singola
    if (!nvRef.current && canvasRef.current) {
      nvRef.current = new Niivue({
        backColor: [0, 0, 0, 1],
        show3Dcrosshair: true,
      });
      nvRef.current.attachToCanvas(canvasRef.current);
    }

    const loadVolume = async () => {
      if (!nvRef.current) return;

      if (nvRef.current.volumes.length > 0) {
        nvRef.current.removeVolume(nvRef.current.volumes[0]);
      }

      let blobUrl = null;

      try {
        if (file) {
          blobUrl = URL.createObjectURL(file);
          await nvRef.current.loadVolumes([{
            url: blobUrl,
            name: file.name,
            colormap: colorMap // Imposta il colore al caricamento
          }]);
        } 
        else if (niftiUrl) {
          const response = await fetch(niftiUrl, {
            headers: { 'Authorization': `Bearer ${token}` }
          });

          if (!response.ok) throw new Error("Accesso negato o file non trovato");

          const blob = await response.blob();
          blobUrl = URL.createObjectURL(blob);
          
          await nvRef.current.loadVolumes([{
            url: blobUrl,
            name: "paziente_storico.nii.gz",
            colormap: colorMap // Imposta il colore al caricamento
          }]);
        }
      } catch (error) {
        console.error("Errore irreversibile nel caricamento NIfTI:", error);
      } finally {
        if (blobUrl) {
          URL.revokeObjectURL(blobUrl);
        }
      }
    };

    loadVolume();

  }, [file, niftiUrl, colorMap, token]); // NB: colorMap NON è qui per evitare doppi caricamenti

  // EFFETTO SEPARATO: Cambia solo il colore in tempo reale senza ricaricare il file
  useEffect(() => {
    if (nvRef.current && nvRef.current.volumes.length > 0) {
      nvRef.current.volumes[0].colormap = colorMap;
      nvRef.current.updateGLVolume();
    }
  }, [colorMap]);

  return (
    <div className="w-full h-full flex flex-col bg-black rounded-xl overflow-hidden">
      <div className="flex-1 relative">
        <canvas ref={canvasRef} className="absolute inset-0 w-full h-full focus:outline-none" />
      </div>
    </div>
  );
};

export default NiiVueCanvas;