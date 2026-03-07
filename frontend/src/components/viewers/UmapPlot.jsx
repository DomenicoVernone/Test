import React from 'react';
import Plot from 'react-plotly.js';

export default function UmapPlot({ data }) {
  // Se non ci sono dati, mostriamo un messaggio di attesa
  if (!data || !data.storico) {
    return (
      <div className="flex items-center justify-center w-full h-full min-h-[400px] text-slate-400">
        In attesa della proiezione spaziale UMAP...
      </div>
    );
  }

  const { storico, nuovo_paziente } = data;

  // 1. ESTRAZIONE DATI GREZZI (Adattamento per Plotly)
  const h_x = Array.isArray(storico) ? storico.map(d => d.x) : storico.x;
  const h_y = Array.isArray(storico) ? storico.map(d => d.y) : storico.y;
  const h_z = Array.isArray(storico) ? storico.map(d => d.z) : storico.z;
  const h_labels = Array.isArray(storico) ? storico.map(d => d.label) : (storico.label || []);

  const n_x = Array.isArray(nuovo_paziente.x) ? nuovo_paziente.x[0] : nuovo_paziente.x;
  const n_y = Array.isArray(nuovo_paziente.y) ? nuovo_paziente.y[0] : nuovo_paziente.y;
  const n_z = Array.isArray(nuovo_paziente.z) ? nuovo_paziente.z[0] : nuovo_paziente.z;

  // 2. SEPARAZIONE DEI CLUSTER (Per rispettare il Punto 5 della Tesi)
  // Creiamo array separati per "Sani" e "Patologici" per avere Traces indipendenti
  const sani_x = [], sani_y = [], sani_z = [];
  const patologici_x = [], patologici_y = [], patologici_z = [];

  for (let i = 0; i < h_labels.length; i++) {
    if (h_labels[i] && h_labels[i].includes('Sano')) {
      sani_x.push(h_x[i]); sani_y.push(h_y[i]); sani_z.push(h_z[i]);
    } else {
      patologici_x.push(h_x[i]); patologici_y.push(h_y[i]); patologici_z.push(h_z[i]);
    }
  }

  // 3. COSTRUZIONE DEI TRACCIATI (Traces)
  const plotData = [
    // TRACE 1: La Nuvola dei Pazienti Sani (Controllo)
    {
      x: sani_x,
      y: sani_y,
      z: sani_z,
      mode: 'markers',
      type: 'scatter3d',
      name: 'Coorte: Sani (HC)',
      hoverinfo: 'name',
      marker: {
        size: 5,
        color: '#10b981', // Verde smeraldo
        opacity: 0.5,     // Semi-trasparente per fare da sfondo
        line: { color: '#059669', width: 0.5 }
      }
    },
    // TRACE 2: La Nuvola dei Pazienti Patologici (Il modello specifico)
    {
      x: patologici_x,
      y: patologici_y,
      z: patologici_z,
      mode: 'markers',
      type: 'scatter3d',
      name: 'Coorte: Patologia', // Il Radar Locale (Punto 3)
      hoverinfo: 'name',
      marker: {
        size: 5,
        color: '#ef4444', // Rosso
        opacity: 0.5,
        line: { color: '#dc2626', width: 0.5 }
      }
    },
    // TRACE 3: Il Paziente Attuale (Target diagnostico)
    {
      x: [n_x],
      y: [n_y],
      z: [n_z],
      mode: 'markers',
      type: 'scatter3d',
      name: '🎯 PAZIENTE IN ESAME',
      text: ['Posizione Spaziale'],
      hoverinfo: 'name',
      marker: {
        size: 14,             // Estremamente visibile
        color: '#3b82f6',     // Blu elettrico
        symbol: 'diamond',    // Forma distintiva (Punto 1)
        line: { color: '#ffffff', width: 3 }, // Bordo spesso bianco
        opacity: 1
      }
    }
  ];

  // 4. CONFIGURAZIONE DELLO SPAZIO 3D (Punto 4)
  const layout = {
    autosize: true,
    margin: { l: 0, r: 0, b: 0, t: 0 },
    scene: {
      xaxis: { title: 'UMAP Dim 1', backgroundcolor: '#f8fafc', gridcolor: '#e2e8f0', showbackground: true, zeroline: false },
      yaxis: { title: 'UMAP Dim 2', backgroundcolor: '#f8fafc', gridcolor: '#e2e8f0', showbackground: true, zeroline: false },
      zaxis: { title: 'UMAP Dim 3', backgroundcolor: '#f8fafc', gridcolor: '#e2e8f0', showbackground: true, zeroline: false },
      camera: { 
        eye: { x: 1.5, y: 1.5, z: 1.2 } // Leggermente inclinato per mostrare bene la profondità
      } 
    },
    legend: { 
      x: 0, y: 1, 
      orientation: 'v',
      bgcolor: 'rgba(255,255,255,0.8)',
      bordercolor: '#e2e8f0',
      borderwidth: 1,
      font: { family: 'sans-serif', size: 12, color: '#334155' }
    },
    paper_bgcolor: 'rgba(0,0,0,0)',
    plot_bgcolor: 'rgba(0,0,0,0)'
  };

  return (
    <div className="w-full h-full min-h-[500px] bg-white rounded-2xl overflow-hidden shadow-inner border border-slate-200 relative">
      <Plot
        data={plotData}
        layout={layout}
        useResizeHandler={true}
        className="w-full h-full absolute inset-0"
        config={{ displayModeBar: true, displaylogo: false, modeBarButtonsToRemove: ['lasso2d', 'select2d'] }} 
      />
    </div>
  );
}