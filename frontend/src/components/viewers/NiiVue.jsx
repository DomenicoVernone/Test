/* eslint-disable react-hooks/exhaustive-deps */
/**
 * Componente Visualizzatore 3D (NIfTI).
 * Sfrutta la libreria @niivue/niivue per il rendering volumetrico.
 * Comunica con il backend asincrono tramite l'istanza Axios centralizzata.
 */
import React, { useEffect, useRef } from 'react';
import { Niivue } from '@niivue/niivue';
import api from '../../services/api';

const NiiVueCanvas = ({ file, niftiUrl, colorMap = 'gray' }) => {
  const canvasRef = useRef(null);
  const nvRef = useRef(null);

  // --- 1. INIZIALIZZAZIONE ENGINE E CARICAMENTO VOLUME ---
  useEffect(() => {
    let isMounted = true;
    let blobUrl = null;

    // Inizializzazione singola dell'engine NiiVue
    if (!nvRef.current && canvasRef.current) {
      nvRef.current = new Niivue({
        backColor: [0, 0, 0, 1],
        show3Dcrosshair: true,
      });
      nvRef.current.attachToCanvas(canvasRef.current);
    }

    const loadVolume = async () => {
      if (!nvRef.current) return;

      // Pulisce i volumi precedenti in modo pulito
      if (nvRef.current.volumes.length > 0) {
        nvRef.current.removeVolume(nvRef.current.volumes[0]);
      }

      try {
        if (file) {
          // Caso 1: File locale
          blobUrl = URL.createObjectURL(file);
          await nvRef.current.loadVolumes([{
            url: blobUrl,
            name: file.name,
            colormap: colorMap 
          }]);
        } 
        else if (niftiUrl) {
          // Caso 2: Download dal backend
          const response = await api.get(niftiUrl, { 
            responseType: 'blob' 
          });
          
          if (!isMounted) return; // Se il componente è stato chiuso durante il download, fermati.

          blobUrl = URL.createObjectURL(response.data);
          await nvRef.current.loadVolumes([{
            url: blobUrl,
            name: "paziente_storico.nii.gz",
            colormap: colorMap 
          }]);
        }
      } catch (error) {
        console.error("🚨 Errore irreversibile nel caricamento NIfTI:", error);
      } 
    };

    loadVolume();

    // Cleanup sicuro
    return () => {
      isMounted = false;
      if (blobUrl) {
        // Il setTimeout salva la vita in React Strict Mode, dando il tempo a NiiVue 
        // di finire il parsing interno prima che il browser distrugga il link.
        setTimeout(() => {
          URL.revokeObjectURL(blobUrl);
        }, 1000);
      }
    };
  }, [file, niftiUrl]); // RIMOSSO colorMap! Il caricamento avviene solo se cambia il file.

  // --- 2. AGGIORNAMENTO COLORE REAL-TIME ---
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