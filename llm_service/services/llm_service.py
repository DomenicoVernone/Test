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
import re
from typing import Dict, Any, List, Tuple
from openai import AsyncOpenAI
from core.config import settings

client = AsyncOpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def calcola_distanza_3d(p1: Dict[str, float], p2: Dict[str, float]) -> float:
    return math.sqrt((p2.get('x', 0) - p1.get('x', 0))**2 + (p2.get('y', 0) - p1.get('y', 0))**2 + (p2.get('z', 0) - p1.get('z', 0))**2)

def normalizza_nome_feature(nome: str) -> str:
    """
    Normalizza i nomi delle feature per garantire il match tra CSV (generato in Python) 
    e JSON (generato in R). R sostituisce spesso '-' e ' ' con '.'.
    Questa funzione converte tutto in minuscolo e rimuove i caratteri speciali comuni.
    """
    nome_pulito = re.sub(r'[^a-zA-Z0-9]', '', nome) # Rimuove tutto tranne lettere e numeri
    return nome_pulito.lower()

def estrai_dati_paziente(task_id: int) -> dict:
    """Legge il CSV ignorando le colonne non numeriche (es. path immagini)."""
    csv_path = os.path.join(settings.FEATURES_DIR, f"features_{task_id}.csv")
    dati_paziente = {}
    
    if not os.path.exists(csv_path):
        print(f"⚠️ CSV non trovato in {csv_path}")
        return dati_paziente
    
    try:
        with open(csv_path, mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)
            values = next(reader)
            
            for h, v in zip(headers, values):
                try:
                    # Tenta la conversione. Se fallisce (è un percorso stringa), ignora.
                    valore_float = float(v)
                    # Normalizza la chiave per il dizionario di Python
                    dati_paziente[normalizza_nome_feature(h)] = {
                        "valore": valore_float,
                        "nome_originale": h 
                    }
                except ValueError:
                    continue
                    
    except Exception as e:
        print(f"🚨 Errore lettura CSV: {e}")
        
    return dati_paziente

def formatta_nome_display(nome_grezzo: str) -> str:
    """Pulisce i nomi delle feature per renderli leggibili nel testo per l'LLM."""
    # Es: "Left-Amygdala_original_shape_Elongation" -> "Left Amygdala Shape Elongation"
    pulito = nome_grezzo.replace("original_", "").replace("_", " ").replace("-", " ")
    return pulito

def analizza_spazio_e_statistiche(json_data: Dict[str, Any], task_id: int, k: int = 15) -> str:
    plot_data = json_data.get("plot_data", {})
    nuovo_paziente = plot_data.get("nuovo_paziente")
    storico = plot_data.get("storico", [])

    if not nuovo_paziente or not storico:
        return "Dati insufficienti per l'analisi RAG (Mancano coordinate spaziali)."

    # 1. Distanze e KNN
    distanze = [{"distanza": calcola_distanza_3d(nuovo_paziente, p), "dati_storici": p} for p in storico]
    distanze.sort(key=lambda item: item["distanza"])
    vicini_top_k = [item["dati_storici"] for item in distanze[:k]]
    
    # Trova l'etichetta dominante nel vicinato
    conteggi = {}
    for v in vicini_top_k:
        label = v.get("label", "Sconosciuto")
        conteggi[label] = conteggi.get(label, 0) + 1
    
    if not conteggi:
        return "Errore topologico: Nessuna etichetta (label) trovata nello storico."
        
    label_dominante = max(conteggi, key=conteggi.get)
    cluster_opposto = [p for p in storico if p.get("label") != label_dominante]

    # 2. Riassunto Topologico
    riassunto = f"[1. TOPOLOGIA SPAZIALE (UMAP)]\n"
    riassunto += f"Dei {k} pazienti storici morfologicamente più simili al caso in esame:\n"
    for label, count in conteggi.items():
        totale_vicini = len(vicini_top_k)
        riassunto += f"- {count} pazienti ({((count/totale_vicini)*100):.1f}%) appartengono al cluster '{str(label).upper()}'.\n"
    riassunto += f"La distanza dal caso storico più affine è {distanze[0]['distanza']:.2f} unità.\n\n"

    # 3. Analisi Statistica Radiomica (Match CSV -> JSON)
    dati_nuovo = estrai_dati_paziente(task_id)
    if not dati_nuovo:
        return riassunto + "\n[ATTENZIONE]: Impossibile estrarre le feature dal file CSV del paziente. L'analisi si baserà solo sulla topologia."

    # Normalizziamo le chiavi del JSON storico per fare il match
    storico_normalizzato = []
    for p in storico:
        p_norm = {normalizza_nome_feature(k): v for k, v in p.items()}
        # Rimettiamo la label che potrebbe essere stata storpiata dalla normalizzazione
        p_norm["label_originale"] = p.get("label") 
        storico_normalizzato.append(p_norm)
        
    vicini_norm = [p for p in storico_normalizzato if p.get("label_originale") == label_dominante]
    opposti_norm = [p for p in storico_normalizzato if p.get("label_originale") != label_dominante]

    riassunto += f"[2. CONFRONTO STATISTICO RADIOMICO (Top Feature Discordanza)]\n"
    riassunto += f"Confronto tra paziente, media Vicinato ({str(label_dominante).upper()}) e media cluster opposto.\n\n"

    feature_processate = 0
    feature_analizzate = [] # Per debug e per evitare doppioni
    
    for key_norm, dict_paziente in dati_nuovo.items():
        val_paziente = dict_paziente["valore"]
        nome_originale = dict_paziente["nome_originale"]
        
        # Estraiamo i valori storici usando la chiave normalizzata
        val_vicini = [v[key_norm] for v in vicini_norm if key_norm in v and isinstance(v[key_norm], (int, float))]
        val_opposti = [v[key_norm] for v in opposti_norm if key_norm in v and isinstance(v[key_norm], (int, float))]

        # Se la feature non esiste nello storico di R, la saltiamo
        if not val_vicini or not val_opposti:
            continue

        media_vicini = statistics.mean(val_vicini)
        std_vicini = statistics.stdev(val_vicini) if len(val_vicini) > 1 else 0.0
        media_opposti = statistics.mean(val_opposti)

        # Calcoliamo la distanza in deviazioni standard per capire quanto è un outlier
        z_score = abs(val_paziente - media_vicini) / std_vicini if std_vicini > 0 else 0
        
        # Ordiniamo le feature per "anomalia" (z-score), per dare all'LLM solo quelle interessanti
        feature_analizzate.append({
            "nome": formatta_nome_display(nome_originale),
            "val_paziente": val_paziente,
            "media_vicini": media_vicini,
            "std_vicini": std_vicini,
            "media_opposti": media_opposti,
            "z_score": z_score
        })

    # Ordiniamo e prendiamo le top 15 più anomale
    feature_analizzate.sort(key=lambda x: x["z_score"], reverse=True)
    top_features = feature_analizzate[:15]

    for f in top_features:
        riassunto += f"- {f['nome']}:\n"
        riassunto += f"  * Paziente in esame : {f['val_paziente']:.3f}\n"
        riassunto += f"  * Media Cluster ({str(label_dominante).upper()}) : {f['media_vicini']:.3f} (± {f['std_vicini']:.3f})\n"
        riassunto += f"  * Media Sani/Opposti: {f['media_opposti']:.3f}\n"
        
    if not top_features:
        riassunto += "Nessuna feature radiomica del CSV è stata trovata nei dati storici del JSON. Assicurati che l'Engine R includa le feature nel referto UMAP."

    return riassunto

async def genera_risposta_medica(task_id: int, messaggio_medico: str) -> str:
    risultati_path = os.path.join(settings.RESULTS_DIR, f"result_{task_id}.json")
    if not os.path.exists(risultati_path):
        return "Errore: Dati clinici non ancora disponibili. Attendere la fine dell'analisi."

    try:
        with open(risultati_path, "r") as f:
            json_data = json.load(f)
    except Exception as e:
        return f"Errore lettura JSON risultati: {e}"

    diagnosi_predetta = json_data.get("diagnosi_predetta", "Sconosciuta")
    contesto_completo = analizza_spazio_e_statistiche(json_data, task_id)

    system_prompt = f"""Sei il Clinical Twin AI, un assistente radiologico integrato (SaMD).
Non emettere MAI diagnosi definitive. Il tuo scopo è interpretare la statistica spaziale e radiomica per supportare il medico.

DATI DEL CASO CORRENTE:
* Esito Modello Machine Learning: {str(diagnosi_predetta).upper()}

{contesto_completo}

ISTRUZIONI:
1. Rispondi alla domanda del medico in italiano in modo professionale e conciso.
2. Spiega PERCHÉ il modello ha preso la decisione, citando la topologia e confrontando al massimo 2 o 3 feature radiomiche chiave (quelle fornite nel contesto) in cui il Paziente si discosta maggiormente dal Vicinato.
3. Regola Matematica: Valuta se il valore del Paziente rientra nell'intervallo [Media - (2 * Dev.Std), Media + (2 * Dev.Std)] del cluster predetto. Se è fuori, dichiara che il paziente presenta un valore ANOMALO (outlier) per quella feature.
4. Concludi ricordando che il medico deve visionare la risonanza grezza NIfTI.
"""

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": messaggio_medico}
            ],
            temperature=0.1,
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Errore motore LLM (Groq): {str(e)}"