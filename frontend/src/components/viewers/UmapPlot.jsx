/**
 * Componente Grafico UMAP 3D (Plotly).
 * Renderizza lo spazio latente calcolato dal motore di inferenza (R).
 * Implementa una logica ibrida per le performance: ResizeObserver nativo 
 * per il debouncing e manipolazione pura del DOM per la dissolvenza visiva.
 * INCLUDE IMPLEMENTAZIONE US-12: Tooltip dinamici con estrazione automatica delle feature.
 */
import React, { useRef, useEffect } from 'react';
import Plot from 'react-plotly.js';

export default function UmapPlot({ data, selectedModel, theme }) {
  const containerRef = useRef(null);
  const fadeRef = useRef(null);

  // --- GESTIONE OTTIMIZZATA RESIZE + DISSOLVENZA (PURE DOM) ---
  useEffect(() => {
    const container = containerRef.current;
    const fadeElement = fadeRef.current;
    if (!container || !fadeElement) return;

    let timeoutId;

    const resizeObserver = new ResizeObserver(() => {
      clearTimeout(timeoutId);
      fadeElement.style.opacity = '0';

      timeoutId = setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        fadeElement.style.opacity = '1';
      }, 300);
    });

    resizeObserver.observe(container);

    return () => {
      resizeObserver.disconnect();
      clearTimeout(timeoutId);
    };
  }, []); 

  if (!data || !data.storico) return null;

  // --- PARSING DATI STRUTTURALI ---
  const { storico, nuovo_paziente } = data;

  const h_x = Array.isArray(storico) ? storico.map(d => d.x) : storico.x;
  const h_y = Array.isArray(storico) ? storico.map(d => d.y) : storico.y;
  const h_z = Array.isArray(storico) ? storico.map(d => d.z) : storico.z;
  const h_labels = Array.isArray(storico) ? storico.map(d => d.label) : (storico.label || []);
  const h_ids = Array.isArray(storico) ? storico.map(d => d.subject_id || 'ID Sconosciuto') : (storico.subject_id || []);

  const n_x = Array.isArray(nuovo_paziente.x) ? nuovo_paziente.x[0] : nuovo_paziente.x;
  const n_y = Array.isArray(nuovo_paziente.y) ? nuovo_paziente.y[0] : nuovo_paziente.y;
  const n_z = Array.isArray(nuovo_paziente.z) ? nuovo_paziente.z[0] : nuovo_paziente.z;

  const isSano = (label) => {
    if (!label) return false;
    const l = label.toString().toLowerCase();
    return l.includes('sano') || l.includes('hc') || l.includes('control');
  };

  // --- ESTRAZIONE DINAMICA DELLE FEATURE CLINICHE (US-12) ---
  // Troviamo le chiavi delle feature ignorando le colonne di servizio
  const keysToIgnore = ['x', 'y', 'z', 'label', 'subject_id', 'label_originale', 'X', 'Y', 'Z'];
  let availableFeatures = [];
  
  if (Array.isArray(storico) && storico.length > 0) {
    availableFeatures = Object.keys(storico[0]).filter(k => !keysToIgnore.includes(k));
  } else if (storico && typeof storico === 'object') {
    availableFeatures = Object.keys(storico).filter(k => !keysToIgnore.includes(k));
  }

  // Selezioniamo solo le prime 3 feature per non ingombrare visivamente il tooltip
  const featuresToDisplay = availableFeatures.slice(0, 5);

  // Funzione helper per rendere leggibili i nomi delle feature
  const formatFeatureName = (name) => {
    // 1. Pulizia base dai suffissi di R (se presenti)
    let cleanName = name.replace(/\.[0-9]+$/, ''); 
    
    // 2. Cerchiamo di dividere le componenti usando gli underscore
    const parts = cleanName.split('_');
    
    if (parts.length >= 3) {
      // Formato Nextflow/PyRadiomics es: "Left-Amygdala_original_firstorder_Energy"
      // parts[0] = "Left-Amygdala"
      // parts[1] = "original"
      // parts[2] = "firstorder"
      // parts[3] = "Energy" (o parts[ultimopezzo])
      
      const anatomy = parts[0].replace(/-/g, ' '); // Trasforma "Left-Amygdala" in "Left Amygdala"
      const metric = parts[parts.length - 1]; // Prende l'ultima parola (es. "Energy", "Skewness")
      
      // Ritorniamo un formato leggibile e compatto: "Left Amygdala: Energy"
      return `${anatomy} ${metric}`;
    }
    
    // Fallback: se la stringa è corta o non ha la struttura standard, puliamola in modo classico
    let fallbackClean = cleanName.replace(/_/g, ' ').replace(/-/g, ' ').replace('original', '').trim();
    return fallbackClean.length > 28 ? fallbackClean.substring(0, 28) + '...' : fallbackClean;
  };

  // --- SEPARAZIONE CLUSTER E CREAZIONE TESTI TOOLTIP ---
  const sani_x = [], sani_y = [], sani_z = [], sani_text = [];
  const patologici_x = [], patologici_y = [], patologici_z = [], patologici_text = [];

  for (let i = 0; i < h_labels.length; i++) {
    const id = h_ids[i] || `Paziente_${i}`;
    const label = h_labels[i];
    
    // Costruiamo la stringa dei biomarcatori dinamicamente
    let featuresHtml = '';
    featuresToDisplay.forEach(featKey => {
      let val = Array.isArray(storico) ? storico[i][featKey] : storico[featKey][i];
      if (typeof val === 'number') val = val.toFixed(3); // Arrotonda a 3 decimali
      featuresHtml += `<br><span style="font-size: 11px; color: #888;">${formatFeatureName(featKey)}:</span> <b>${val}</b>`;
    });
    
    const hoverText = `<b>ID:</b> ${id}<br><b>Classificazione:</b> ${label.toUpperCase()}${featuresHtml}`;

    if (isSano(h_labels[i])) {
      sani_x.push(h_x[i]); sani_y.push(h_y[i]); sani_z.push(h_z[i]);
      sani_text.push(hoverText);
    } else {
      patologici_x.push(h_x[i]); patologici_y.push(h_y[i]); patologici_z.push(h_z[i]);
      patologici_text.push(hoverText);
    }
  }

  // Costruiamo il tooltip anche per il nuovo paziente
  let newPatientFeaturesHtml = '';
  featuresToDisplay.forEach(featKey => {
    let val = Array.isArray(nuovo_paziente[featKey]) ? nuovo_paziente[featKey][0] : nuovo_paziente[featKey];
    
    // FIX DI SICUREZZA: Gestione dei valori mancanti (evita crash o NaN)
    if (typeof val === 'number') {
      val = val.toFixed(3);
    } else if (val === undefined || val === null) {
      val = 'N/A';
    }

    newPatientFeaturesHtml += `<br><span style="font-size: 11px; color: #888;">${formatFeatureName(featKey)}:</span> <b>${val}</b>`;
  });
  
  const hoverTextNuovo = `<b>ID:</b> Paziente in Esame<br><b>Stato:</b> Da Diagnosticare${newPatientFeaturesHtml}`;

  const modelName = selectedModel ? selectedModel.replace('HC_vs_', '') : 'Patologia';

  // --- DEFINIZIONE TRACCE PLOTLY ---
  const plotData = [
    {
      x: sani_x, y: sani_y, z: sani_z,
      mode: 'markers', type: 'scatter3d',
      name: 'Coorte: Sani (HC)',
      text: sani_text,
      hovertemplate: '%{text}<extra></extra>',
      marker: { size: 5, color: '#10b981', opacity: 0.5, line: { color: '#059669', width: 0.5 } }
    },
    {
      x: patologici_x, y: patologici_y, z: patologici_z,
      mode: 'markers', type: 'scatter3d',
      name: `Coorte: ${modelName}`,
      text: patologici_text,
      hovertemplate: '%{text}<extra></extra>', 
      marker: { size: 5, color: '#ef4444', opacity: 0.5, line: { color: '#dc2626', width: 0.5 } }
    },
    {
      x: [n_x], y: [n_y], z: [n_z],
      mode: 'markers', type: 'scatter3d',
      name: '🎯 PAZIENTE IN ESAME',
      text: [hoverTextNuovo], 
      hovertemplate: '%{text}<extra></extra>',
      marker: { size: 14, color: '#3b82f6', symbol: 'circle', line: { color: '#ffffff', width: 3 }, opacity: 1 }
    }
  ];

  // --- STILIZZAZIONE E TEMI ---
  const isDark = theme === 'dark';
  const wallColor = isDark ? '#1e293b' : '#f8fafc'; 
  const gridColor = isDark ? '#334155' : '#e2e8f0'; 
  const fontColor = isDark ? '#cbd5e1' : '#334155'; 
  const legendBg = isDark ? 'rgba(30,41,59,0.8)' : 'rgba(255,255,255,0.8)'; 
  const tooltipBg = isDark ? '#1e293b' : '#ffffff';

  const axisStyle = { 
    title: '', 
    backgroundcolor: wallColor, 
    gridcolor: gridColor, 
    showbackground: true, 
    zeroline: false,
    tickfont: { color: fontColor }
  };

  const layout = {
    autosize: true, 
    margin: { l: 0, r: 0, b: 0, t: 0 }, 
    font: { color: fontColor },
    hoverlabel: {
      bgcolor: tooltipBg,
      font: { color: fontColor, family: 'Inter, sans-serif', size: 13 },
      bordercolor: isDark ? '#475569' : '#cbd5e1',
    },
    scene: {
      xaxis: axisStyle,
      yaxis: axisStyle,
      zaxis: axisStyle,
      camera: { eye: { x: 1.5, y: 1.5, z: 1.2 } }
    },
    legend: { x: 0, y: 1, orientation: 'v', bgcolor: legendBg, font: { color: fontColor } },
    paper_bgcolor: 'rgba(0,0,0,0)', 
    plot_bgcolor: 'rgba(0,0,0,0)'   
  };

  return (
    <div ref={containerRef} className="w-full h-full flex-1 min-h-0 relative overflow-hidden">
      <div ref={fadeRef} className="w-full h-full transition-opacity duration-1000 ease-in-out" style={{ opacity: 1 }}>
        <Plot
          data={plotData}
          layout={layout}
          useResizeHandler={true} 
          style={{ width: "100%", height: "100%" }} 
          config={{ displayModeBar: false, responsive: true }}
        />
      </div>
    </div>
  );
}
