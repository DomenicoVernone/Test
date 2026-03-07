import React, { useEffect, useRef, useContext } from 'react';
import { Niivue } from '@niivue/niivue';
import { AuthContext } from '../../contexts/AuthContext'; 

const NiiVueCanvas = ({ file, niftiUrl }) => {
  const canvasRef = useRef(null);
  const nvRef = useRef(null);
  const { token } = useContext(AuthContext); 

  useEffect(() => {
    // Inizializzazione singola del motore 3D
    if (!nvRef.current && canvasRef.current) {
      nvRef.current = new Niivue({
        backColor: [0, 0, 0, 1],
        show3Dcrosshair: true,
      });
      nvRef.current.attachToCanvas(canvasRef.current);
    }

    const loadVolume = async () => {
      if (!nvRef.current) return;

      // Pulisci il volume precedente per non sovrapporre i cervelli
      if (nvRef.current.volumes.length > 0) {
        nvRef.current.removeVolume(nvRef.current.volumes[0]);
      }

      let blobUrl = null; // Il nostro finto URL temporaneo

      try {
        // 1. CARICAMENTO FILE LOCALE (Nuovo Upload dal PC)
        if (file) {
          blobUrl = URL.createObjectURL(file);
          
          await nvRef.current.loadVolumes([{
            url: blobUrl,
            name: file.name // NiiVue legge l'estensione da qui
          }]);
        } 
        
        // 2. CARICAMENTO DALLO STORICO (Rete + Token)
        else if (niftiUrl) {
          // Scarichiamo noi il file usando il Token per bypassare l'errore 401
          const response = await fetch(niftiUrl, {
            headers: { 'Authorization': `Bearer ${token}` }
          });

          if (!response.ok) throw new Error("Accesso negato o file non trovato");

          // Trasformiamo la risposta in un Blob (dati binari grezzi)
          const blob = await response.blob();
          
          // Creiamo un URL fittizio che punta alla RAM del browser
          blobUrl = URL.createObjectURL(blob);
          
          // Passiamo tutto a NiiVue!
          await nvRef.current.loadVolumes([{
            url: blobUrl,
            name: "paziente_storico.nii.gz" // NiiVue capisce che è zippato e non crasha
          }]);
        }
      } catch (error) {
        console.error("Errore irreversibile nel caricamento NIfTI:", error);
      } finally {
        // Buona pratica: puliamo la memoria del browser dopo aver caricato il 3D
        if (blobUrl) {
          URL.revokeObjectURL(blobUrl);
        }
      }
    };

    loadVolume();

  }, [file, niftiUrl, token]); 

  return (
    <div className="w-full h-full flex flex-col bg-black rounded-xl overflow-hidden">
      <div className="flex-1 relative">
        <canvas ref={canvasRef} className="absolute inset-0 w-full h-full focus:outline-none" />
      </div>
    </div>
  );
};

export default NiiVueCanvas;