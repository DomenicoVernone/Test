import React, { useEffect, useRef } from 'react';
import { Niivue } from 'https://esm.sh/@niivue/niivue';

const NiiVueCanvas = ({ file, niftiUrl }) => {
  const canvasRef = useRef(null);
  const nvRef = useRef(null);

  useEffect(() => {
    // Inizializza Niivue se non esiste
    if (!nvRef.current && canvasRef.current) {
      nvRef.current = new Niivue({
        backColor: [0, 0, 0, 1],
        show3Dcrosshair: true,
      });
      nvRef.current.attachToCanvas(canvasRef.current);
    }

    const loadVolume = async () => {
      if (nvRef.current) {
        // Se c'è un file locale (Nuovo Upload)
        if (file) {
          const reader = new FileReader();
          reader.onload = async (e) => {
            const buffer = e.target.result;
            const volume = {
              name: file.name,
              dataBuffer: buffer,
            };
            await nvRef.current.loadVolumes([volume]);
          };
          reader.readAsArrayBuffer(file);
        } 
        // Se c'è un URL (Caricamento dallo Storico)
        else if (niftiUrl) {
          try {
            // Niivue gestisce automaticamente il fetching dalla rete
            await nvRef.current.loadVolumes([{ url: niftiUrl }]);
          } catch (error) {
            console.error("Errore nel caricamento del NIfTI di rete:", error);
          }
        }
      }
    };

    loadVolume();

  }, [file, niftiUrl]); // Si attiva ogni volta che cambia il file locale o l'URL

  return (
    <div className="w-full h-full flex flex-col bg-black">
      <div className="flex-1 relative">
        <canvas ref={canvasRef} className="absolute inset-0 w-full h-full focus:outline-none" />
      </div>
    </div>
  );
};

export default NiiVueCanvas;