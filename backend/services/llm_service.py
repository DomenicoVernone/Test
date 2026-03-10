# File: backend/services/llm_service.py
"""
Servizio LLM Context-Aware Ibrido Avanzato.
Incrocia la topologia UMAP (JSON) con le feature radiomiche reali (CSV).
Implementa un calcolo statistico scalabile (Media + Dev. Standard) su modelli dinamici.
"""
import math
import os
import json
import csv
import statistics
from typing import Dict, Any, List, Tuple
from openai import AsyncOpenAI
from core.config import settings

client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def calcola_distanza_3d(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return math.sqrt((p2['x'] - p1['x'])**2 + (p2['y'] - p1['y'])**2 + (p2['z'] - p1['z'])**2)

def estrai_dati_paziente(task_id: int) -> dict:
    """Legge il CSV per ottenere il dizionario esatto Feature -> Valore del nuovo paziente."""
    csv_path = os.path.join(settings.FEATURES_DIR, f"features_{task_id}.csv")
    dati_paziente = {}
    if not os.path.exists(csv_path):
        return dati_paziente
    
    try:
        with open(csv_path, mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)
            values = next(reader)
            for h, v in zip(headers, values):
                dati_paziente[h] = float(v)
    except Exception as e:
        print(f"Errore lettura CSV: {e}")
        
    return dati_paziente

def formatta_nome_feature(nome_greco: str) -> str:
    """Pulisce i nomi delle feature per renderli leggibili all'LLM."""
    return nome_greco.replace("original_", "").replace("_", " ")

def analizza_spazio_e_statistiche(json_data: Dict[str, Any], task_id: int, k: int = 15) -> str:
    plot_data = json_data.get("plot_data", {})
    nuovo_paziente = plot_data.get("nuovo_paziente")
    storico = plot_data.get("storico", [])

    if not nuovo_paziente or not storico:
        return "Dati insufficienti per l'analisi RAG."

    # 1. Distanze e KNN
    distanze = [{"distanza": calcola_distanza_3d(nuovo_paziente, p), "dati_storici": p} for p in storico]
    distanze.sort(key=lambda item: item["distanza"])
    vicini_top_k = [item["dati_storici"] for item in distanze[:k]]
    
    # Trova l'etichetta dominante nel vicinato
    conteggi = {}
    for v in vicini_top_k:
        conteggi[v["label"]] = conteggi.get(v["label"], 0) + 1
    label_dominante = max(conteggi, key=conteggi.get)

    # Identifica il cluster opposto globale per fare contrasto clinico
    cluster_opposto = [p for p in storico if p["label"] != label_dominante]

    # 2. Riassunto Topologico
    riassunto = f"[1. TOPOLOGIA SPAZIALE (UMAP)]\n"
    riassunto += f"Dei {k} pazienti storici morfologicamente più simili al caso in esame:\n"
    for label, count in conteggi.items():
        riassunto += f"- {count} pazienti ({((count/k)*100):.1f}%) appartengono al cluster '{label.upper()}'.\n"
    riassunto += f"La distanza dal caso storico più affine è {distanze[0]['distanza']:.2f} unità.\n\n"

    # 3. Analisi Statistica Scalabile delle Feature (CSV + JSON)
    dati_nuovo = estrai_dati_paziente(task_id)
    if not dati_nuovo:
        return riassunto + "Dati radiomici grezzi non trovati."

    riassunto += f"[2. CONFRONTO STATISTICO RADIOMICO]\n"
    riassunto += f"Di seguito il confronto tra le feature del paziente in esame, la media (± deviazione standard) del suo Vicinato, e la media del cluster opposto.\n\n"

    for feature, val_paziente in dati_nuovo.items():
        # Estrai i valori di questa feature per i due gruppi
        val_vicini = [v[feature] for v in vicini_top_k if feature in v]
        val_opposti = [v[feature] for v in cluster_opposto if feature in v]

        media_vicini = statistics.mean(val_vicini) if val_vicini else 0.0
        std_vicini = statistics.stdev(val_vicini) if len(val_vicini) > 1 else 0.0
        media_opposti = statistics.mean(val_opposti) if val_opposti else 0.0

        nome_pulito = formatta_nome_feature(feature)
        
        riassunto += f"- {nome_pulito}:\n"
        riassunto += f"  * Paziente in esame : {val_paziente:.3f}\n"
        riassunto += f"  * Vicinato ({label_dominante.upper()}) : {media_vicini:.3f} (± {std_vicini:.3f})\n"
        riassunto += f"  * Media Sani/Opposti: {media_opposti:.3f}\n"

    return riassunto

async def genera_risposta_medica(task_id: int, messaggio_medico: str) -> str:
    risultati_path = os.path.join(settings.RESULTS_DIR, f"result_{task_id}.json")
    if not os.path.exists(risultati_path):
        return "Errore: Dati clinici non ancora disponibili."

    with open(risultati_path, "r") as f:
        json_data = json.load(f)

    diagnosi_predetta = json_data.get("diagnosi_predetta", "Sconosciuta")
    contesto_completo = analizza_spazio_e_statistiche(json_data, task_id)

    system_prompt = f"""Sei il Clinical Twin AI, un assistente radiologico integrato (SaMD).
Non emettere MAI diagnosi definitive. Il tuo scopo è interpretare la statistica spaziale e radiomica per supportare il medico.

DATI DEL CASO CORRENTE:
* Esito Modello Random Forest: {diagnosi_predetta.upper()}

{contesto_completo}

ISTRUZIONI:
1. Rispondi alla domanda del medico in italiano in modo professionale.
2. Spiega PERCHÉ il modello ha preso la decisione, citando le distanze spaziali e confrontando 2 o 3 feature radiomiche chiave del Paziente con le Medie (e deviazioni standard) del Vicinato e del Cluster Opposto.
3. Regola Matematica Ferrea: Valuta mentalmente se il valore del Paziente è strettamente compreso nell'intervallo [Media - Dev.Std, Media + Dev.Std] del cluster predetto. Se NON lo è, devi dichiarare esplicitamente al medico che il paziente presenta un valore ANOMALO (outlier) per quella feature rispetto al cluster assegnato, senza cercare di giustificarlo forzatamente.
4. Concludi ricordando che il medico deve visionare l'MRI grezza.
"""

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": messaggio_medico}
            ],
            temperature=0.1,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore motore LLM: {str(e)}"