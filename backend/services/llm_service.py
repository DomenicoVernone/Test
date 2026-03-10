# File: backend/services/llm_service.py
"""
Servizio LLM Context-Aware (Spatial RAG).
Calcola la topologia locale del paziente nello spazio latente UMAP 
e inietta i dati in un prompt strutturato per l'assistente AI.
"""
import math
import os
import json
from typing import Dict, Any
from openai import AsyncOpenAI
from core.config import settings

# Inizializza il client OpenAI puntando al Base URL di Groq (Dependency Injection)
client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def calcola_distanza_3d(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    """Calcola la distanza euclidea tridimensionale tra due punti."""
    return math.sqrt(
        (p2['x'] - p1['x'])**2 + 
        (p2['y'] - p1['y'])**2 + 
        (p2['z'] - p1['z'])**2
    )

def analizza_vicinato_paziente(json_data: Dict[str, Any], k: int = 15) -> str:
    """Esegue l'algoritmo K-Nearest Neighbors (KNN) logico nello spazio latente UMAP."""
    plot_data = json_data.get("plot_data", {})
    nuovo_paziente = plot_data.get("nuovo_paziente")
    storico = plot_data.get("storico", [])

    if not nuovo_paziente or not storico:
        return "Dati spaziali non sufficienti per l'analisi del vicinato."

    distanze = []
    for p_storico in storico:
        d = calcola_distanza_3d(nuovo_paziente, p_storico)
        distanze.append({"distanza": d, "label": p_storico["label"]})

    distanze.sort(key=lambda item: item["distanza"])
    vicini = distanze[:k]
    
    conteggio_etichette = {}
    for vicino in vicini:
        label = vicino["label"]
        conteggio_etichette[label] = conteggio_etichette.get(label, 0) + 1

    riassunto = f"Analisi Spaziale K-Nearest Neighbors (K={k}):\n"
    for label, count in conteggio_etichette.items():
        percentuale = (count / k) * 100
        riassunto += f"- {count} pazienti ({percentuale:.1f}%) appartengono al cluster '{label}'.\n"

    riassunto += f"La distanza dal caso storico più simile è {vicini[0]['distanza']:.2f} unità.\n"
    return riassunto


async def genera_risposta_medica(task_id: int, messaggio_medico: str) -> str:
    """
    Carica i dati del paziente, calcola la matematica spaziale e interroga l'LLM.
    """
    # 1. Carica il JSON generato dalla pipeline
    risultati_path = os.path.join(settings.RESULTS_DIR, f"result_{task_id}.json")
    if not os.path.exists(risultati_path):
        return "Errore: Dati clinici non ancora disponibili. Attendi la fine della pipeline."

    with open(risultati_path, "r") as f:
        json_data = json.load(f)

    diagnosi_predetta = json_data.get("diagnosi_predetta", "Sconosciuta")
    
    # 2. Calcola lo Spazio (Il nostro "trucco" da Data Scientist)
    contesto_spaziale = analizza_vicinato_paziente(json_data)

    # 3. Costruisci i Guardrails (Il Prompt di Sistema)
    system_prompt = f"""Sei un assistente bioinformatico integrato in un software radiologico (SaMD).
Regola Primaria: NON SEI UN MEDICO. Non emettere diagnosi cliniche finali. Interpreta solo i dati statistici spaziali.

DATI DEL PAZIENTE ATTUALE:
- Classificazione predetta: {diagnosi_predetta.upper()}
- Topologia UMAP:
{contesto_spaziale}

Istruzioni: Rispondi alla domanda del medico in italiano, in modo rigoroso. Usa i dati spaziali per giustificare la risposta."""

    # 4. Inferenza AI (Chiamata a Groq con LLaMA 3)
    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": messaggio_medico}
            ],
            temperature=0.2, # Temperatura bassa = Risposte più analitiche e meno fantasiose
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore di comunicazione con il motore LLM: {str(e)}"