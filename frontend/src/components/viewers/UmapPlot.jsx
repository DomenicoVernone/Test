/**
 * Componente Grafico UMAP 3D (Plotly).
 * Renderizza lo spazio latente calcolato dal motore R, posizionando
 * il paziente corrente rispetto alle coorti storiche (Sani vs Patologici).
 *
 * @param {Object} props
 * @param {Object} props.data - JSON con coordinate { storico: [...], nuovo_paziente: {...} }
 * @param {string} props.selectedModel - Nome del modello per l'etichetta legenda.
 * @param {string} props.theme - Tema grafico ('light' o 'dark').
 */
import React from 'react';
import Plot from 'react-plotly.js';

export default function UmapPlot({ data, selectedModel, theme }) {
  if (!data || !data.storico) return null;

  const { storico, nuovo_paziente } = data;

  const h_x = Array.isArray(storico) ? storico.map(d => d.x) : storico.x;
  const h_y = Array.isArray(storico) ? storico.map(d => d.y) : storico.y;
  const h_z = Array.isArray(storico) ? storico.map(d => d.z) : storico.z;
  const h_labels = Array.isArray(storico) ? storico.map(d => d.label) : (storico.label || []);

  const n_x = Array.isArray(nuovo_paziente.x) ? nuovo_paziente.x[0] : nuovo_paziente.x;
  const n_y = Array.isArray(nuovo_paziente.y) ? nuovo_paziente.y[0] : nuovo_paziente.y;
  const n_z = Array.isArray(nuovo_paziente.z) ? nuovo_paziente.z[0] : nuovo_paziente.z;

  const isSano = (label) => {
    if (!label) return false;
    const l = label.toString().toLowerCase();
    return l.includes('sano') || l.includes('hc') || l.includes('control');
  };

  const sani_x = [], sani_y = [], sani_z = [];
  const patologici_x = [], patologici_y = [], patologici_z = [];

  for (let i = 0; i < h_labels.length; i++) {
    if (isSano(h_labels[i])) {
      sani_x.push(h_x[i]); sani_y.push(h_y[i]); sani_z.push(h_z[i]);
    } else {
      patologici_x.push(h_x[i]); patologici_y.push(h_y[i]); patologici_z.push(h_z[i]);
    }
  }

  const modelName = selectedModel ? selectedModel.replace('HC_vs_', '') : 'Patologia';

  const plotData = [
    {
      x: sani_x, y: sani_y, z: sani_z,
      mode: 'markers', type: 'scatter3d',
      name: 'Coorte: Sani (HC)',
      hoverinfo: 'name',
      marker: { size: 5, color: '#10b981', opacity: 0.5, line: { color: '#059669', width: 0.5 } }
    },
    {
      x: patologici_x, y: patologici_y, z: patologici_z,
      mode: 'markers', type: 'scatter3d',
      name: `Coorte: ${modelName}`,
      hoverinfo: 'name',
      marker: { size: 5, color: '#ef4444', opacity: 0.5, line: { color: '#dc2626', width: 0.5 } }
    },
    {
      x: [n_x], y: [n_y], z: [n_z],
      mode: 'markers', type: 'scatter3d',
      name: '🎯 PAZIENTE IN ESAME',
      text: ['Posizione Spaziale'], hoverinfo: 'name',
      marker: { size: 14, color: '#3b82f6', symbol: 'diamond', line: { color: '#ffffff', width: 3 }, opacity: 1 }
    }
  ];

  const isDark = theme === 'dark';
  const wallColor = isDark ? '#1e293b' : '#f8fafc'; 
  const gridColor = isDark ? '#334155' : '#e2e8f0'; 
  const fontColor = isDark ? '#cbd5e1' : '#334155'; 
  const legendBg = isDark ? 'rgba(30,41,59,0.8)' : 'rgba(255,255,255,0.8)'; 

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
    <div className="w-full h-full absolute inset-0">
      <Plot
        data={plotData}
        layout={layout}
        useResizeHandler={true}
        className="w-full h-full"
        config={{ displayModeBar: false }}
      />
    </div>
  );
}