import React, { useRef, useEffect } from 'react';
import { Niivue } from 'https://esm.sh/@niivue/niivue';

const NiiVue = ({ file }) => {
  const canvasRef = useRef(null);
  const nvRef = useRef(null);

  useEffect(() => {
    if (!nvRef.current && canvasRef.current) {
      const nv = new Niivue({
        logging: false,
        dragAndDropEnabled: false,
        backColor: [0, 0, 0, 1], 
        show3Dcrosshair: true,    
        loadingText: "Caricamento volume anatomico in corso...",

        multiplanarShowRender: false, 
      });
      
      nv.attachToCanvas(canvasRef.current);
      nvRef.current = nv;
    }
  }, []);

  useEffect(() => {
    if (file && nvRef.current) {
      console.log("NiiVue sta caricando:", file.name);
      
      while (nvRef.current.volumes.length > 0) {
        nvRef.current.removeVolume(nvRef.current.volumes[0]);
      }
      
      nvRef.current.loadFromFile(file).catch(err => {
        console.error("Errore critico nel caricamento NiiVue:", err);
      });
    }
  }, [file]);


  return (
    <div className="relative w-full h-full bg-black overflow-hidden rounded-xl shadow-inner">
      <canvas 
        ref={canvasRef} 
        className="w-full h-full outline-none block" 
      />
    </div>
  );
};

export default NiiVue;