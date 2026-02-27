import { useState } from 'react';

function App() {
  const [messaggio, setMessaggio] = useState("Pronto per l'analisi");

  const eseguiAnalisi = async () => {
    setMessaggio("Chiamata alla pipeline in corso...");
    try {
        const response = await fetch('http://localhost:8000/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ patient_id: 1 })
        });
        const data = await response.json();
        // data.dati_clinici.probability_FTD[0] contiene il valore da R!
        setMessaggio(`Diagnosi: Probabilità FTD ${data.dati_clinici.probability_FTD[0] * 100}%`);
    } catch {
        setMessaggio("Errore: il backend non risponde");
    }
};

  return (
    <div style={{ padding: '20px', textAlign: 'center' }}>
      <h1>Dashboard Clinica FTD</h1>
      <div className="bg-red-500 text-white p-10">Test Tailwind!</div>
      <button onClick={eseguiAnalisi} style={{ padding: '10px 20px', cursor: 'pointer' }}>
        Avvia Diagnosi su Pipeline Docker
      </button>
      <div style={{ marginTop: '20px', fontWeight: 'bold' }}>
        {messaggio}
      </div>
    </div>
  );
}

export default App;