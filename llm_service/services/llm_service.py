# File: llm_service/services/llm_service.py
#
# Logica centrale del servizio LLM context-aware.
# Per ogni richiesta di chat:
#   1. Legge il JSON dei risultati della pipeline (coordinate UMAP + diagnosi predetta).
#   2. Calcola il vicinato k-NN nello spazio UMAP e identifica il cluster dominante.
#   3. Incrocia le feature radiomiche del paziente (CSV) con le statistiche del vicinato (JSON).
#   4. Costruisce un system prompt con il contesto clinico e lo invia a Groq (LLaMA 3.1-8b).
#
# La memoria multi-turno è gestita lato client: la history viene passata esplicitamente
# ad ogni chiamata e anteposta al messaggio corrente, con il system prompt sempre in testa.

import csv
import json
import logging
import math
import os
import re
import statistics
from typing import Any, Dict, List

from openai import AsyncOpenAI

from core.config import settings

logger = logging.getLogger(__name__)

# Il client Groq è compatibile con l'SDK OpenAI: basta sovrascrivere base_url.
client = AsyncOpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)


def calcola_distanza_3d(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return math.sqrt(
        (p2.get("x", 0) - p1.get("x", 0)) ** 2 +
        (p2.get("y", 0) - p1.get("y", 0)) ** 2 +
        (p2.get("z", 0) - p1.get("z", 0)) ** 2
    )


def normalizza_nome_feature(nome: str) -> str:
    """
    Normalizza i nomi delle feature per garantire il match tra CSV (Python) e JSON (R).
    R sostituisce spazi e trattini con punti; questa funzione rimuove tutti i caratteri
    non alfanumerici e converte in minuscolo, rendendo i due formati confrontabili.
    Limite noto: nomi molto simili possono collidere dopo la normalizzazione.
    """
    return re.sub(r"[^a-zA-Z0-9]", "", nome).lower()


def estrai_dati_paziente(task_id: int) -> dict:
    """Legge il CSV delle feature del paziente, ignorando le colonne non numeriche."""
    csv_path = os.path.join(settings.FEATURES_DIR, f"features_{task_id}.csv")
    dati_paziente = {}

    if not os.path.exists(csv_path):
        logger.warning(f"CSV features non trovato: {csv_path}")
        return dati_paziente

    try:
        with open(csv_path, mode="r") as file:
            reader = csv.reader(file)
            headers = next(reader)
            values = next(reader)

            for h, v in zip(headers, values):
                try:
                    dati_paziente[normalizza_nome_feature(h)] = {
                        "valore": float(v),
                        "nome_originale": h,
                    }
                except ValueError:
                    continue
    except Exception as e:
        logger.error(f"Errore lettura CSV features task {task_id}: {e}")

    return dati_paziente


def formatta_nome_display(nome_grezzo: str) -> str:
    """Rende leggibile il nome di una feature radiomica rimuovendo prefissi e separatori."""
    return nome_grezzo.replace("original_", "").replace("_", " ").replace("-", " ")


def analizza_spazio_e_statistiche(json_data: Dict[str, Any], task_id: int, k: int = 15) -> str:
    plot_data = json_data.get("plot_data", {})
    nuovo_paziente = plot_data.get("nuovo_paziente")
    storico = plot_data.get("storico", [])

    if not nuovo_paziente or not storico:
        return "Dati insufficienti per l'analisi RAG: coordinate spaziali mancanti."

    # Calcolo k-NN nello spazio UMAP
    distanze = sorted(
        [{"distanza": calcola_distanza_3d(nuovo_paziente, p), "dati_storici": p} for p in storico],
        key=lambda item: item["distanza"],
    )
    vicini_top_k = [item["dati_storici"] for item in distanze[:k]]

    conteggi: Dict[str, int] = {}
    for v in vicini_top_k:
        label = v.get("label", "Sconosciuto")
        conteggi[label] = conteggi.get(label, 0) + 1

    if not conteggi:
        return "Errore topologico: nessuna etichetta trovata nello storico."

    label_dominante = max(conteggi, key=conteggi.get)

    riassunto = "[1. TOPOLOGIA SPAZIALE (UMAP)]\n"
    riassunto += f"Dei {k} pazienti storici morfologicamente piu' simili al caso in esame:\n"
    for label, count in conteggi.items():
        pct = (count / len(vicini_top_k)) * 100
        riassunto += f"- {count} pazienti ({pct:.1f}%) appartengono al cluster '{str(label).upper()}'.\n"
    riassunto += f"La distanza dal caso storico piu' affine e' {distanze[0]['distanza']:.2f} unita'.\n\n"

    # Confronto statistico radiomico: CSV paziente vs statistiche del vicinato
    dati_nuovo = estrai_dati_paziente(task_id)
    if not dati_nuovo:
        return riassunto + "\n[ATTENZIONE]: Feature CSV non disponibili. L'analisi e' basata solo sulla topologia."

    storico_normalizzato = []
    for p in storico:
        p_norm = {normalizza_nome_feature(k_): v for k_, v in p.items()}
        p_norm["label_originale"] = p.get("label")
        storico_normalizzato.append(p_norm)

    vicini_norm = [p for p in storico_normalizzato if p.get("label_originale") == label_dominante]
    opposti_norm = [p for p in storico_normalizzato if p.get("label_originale") != label_dominante]

    riassunto += "[2. CONFRONTO STATISTICO RADIOMICO (Top Feature per Discordanza)]\n"
    riassunto += f"Confronto tra paziente, media vicinato ({str(label_dominante).upper()}) e media cluster opposto.\n\n"

    feature_analizzate = []

    for key_norm, dict_paziente in dati_nuovo.items():
        val_paziente = dict_paziente["valore"]
        nome_originale = dict_paziente["nome_originale"]

        val_vicini = [
            v[key_norm] for v in vicini_norm
            if key_norm in v and isinstance(v[key_norm], (int, float))
        ]
        val_opposti = [
            v[key_norm] for v in opposti_norm
            if key_norm in v and isinstance(v[key_norm], (int, float))
        ]

        if not val_vicini or not val_opposti:
            continue

        media_vicini = statistics.mean(val_vicini)
        std_vicini = statistics.stdev(val_vicini) if len(val_vicini) > 1 else 0.0
        media_opposti = statistics.mean(val_opposti)
        z_score = abs(val_paziente - media_vicini) / std_vicini if std_vicini > 0 else 0.0

        feature_analizzate.append({
            "nome": formatta_nome_display(nome_originale),
            "val_paziente": val_paziente,
            "media_vicini": media_vicini,
            "std_vicini": std_vicini,
            "media_opposti": media_opposti,
            "z_score": z_score,
        })

    feature_analizzate.sort(key=lambda x: x["z_score"], reverse=True)
    top_features = feature_analizzate[:15]

    for f in top_features:
        riassunto += f"- {f['nome']}:\n"
        riassunto += f"  * Paziente       : {f['val_paziente']:.3f}\n"
        riassunto += f"  * Media {str(label_dominante).upper()} : {f['media_vicini']:.3f} (+/- {f['std_vicini']:.3f})\n"
        riassunto += f"  * Media opposti  : {f['media_opposti']:.3f}\n"

    if not top_features:
        riassunto += (
            "Nessuna feature del CSV corrisponde ai dati storici del JSON. "
            "Verificare che l'inference engine R includa le feature nel referto UMAP."
        )

    return riassunto


async def genera_risposta_medica(
    task_id: int,
    messaggio_medico: str,
    history: List[Dict[str, str]] = [],
) -> str:
    """
    Genera una risposta clinica contestualizzata combinando topologia UMAP
    e analisi radiomica. Il system prompt con il contesto del caso viene sempre
    inserito come primo messaggio, garantendo che l'LLM mantenga il riferimento
    ai dati del paziente attraverso tutta la conversazione multi-turno.
    """
    risultati_path = os.path.join(settings.RESULTS_DIR, f"result_{task_id}.json")
    if not os.path.exists(risultati_path):
        return "Errore: dati clinici non ancora disponibili. Attendere la fine dell'analisi."

    try:
        with open(risultati_path, "r") as f:
            json_data = json.load(f)
    except Exception as e:
        return f"Errore lettura JSON risultati: {e}"

    diagnosi_predetta = json_data.get("diagnosi_predetta", "Sconosciuta")
    contesto_completo = analizza_spazio_e_statistiche(json_data, task_id)

    system_prompt = f"""Sei il Clinical Twin AI, un assistente radiologico integrato (SaMD).
Non emettere MAI diagnosi definitive. Il tuo scopo e' interpretare la statistica spaziale e radiomica per supportare il medico.

DATI DEL CASO CORRENTE:
* Esito Modello Machine Learning: {str(diagnosi_predetta).upper()}

{contesto_completo}

ISTRUZIONI:
1. Rispondi alla domanda del medico in italiano in modo professionale e conciso.
2. Spiega PERCHE' il modello ha preso la decisione, citando la topologia e confrontando al massimo 2 o 3 feature radiomiche chiave in cui il paziente si discosta maggiormente dal vicinato.
3. Regola matematica: valuta se il valore del paziente rientra nell'intervallo [Media - 2*Dev.Std, Media + 2*Dev.Std] del cluster predetto. Se e' fuori, dichiara il valore ANOMALO (outlier).
4. Concludi ricordando che il medico deve visionare la risonanza grezza NIfTI.
"""

    # Struttura messaggi: [system] → [history turni precedenti] → [messaggio corrente]
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": messaggio_medico})

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.1,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Errore Groq API task {task_id}: {e}")
        return f"Errore motore LLM (Groq): {str(e)}"
