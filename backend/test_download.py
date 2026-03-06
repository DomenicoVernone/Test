import os
from dotenv import load_dotenv
import mlflow
from mlflow.tracking import MlflowClient

# 1. Carica le credenziali
load_dotenv()
dagshub_user = os.environ.get("DAGSHUB_USERNAME")
dagshub_token = os.environ.get("MLFLOW_TRACKING_PASSWORD")

os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_user
os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

MLFLOW_TRACKING_URI = "https://dagshub.com/donatooooooo/FTD_diagnosis.mlflow"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

client = MlflowClient()

print("🔍 Scannerizzazione del Model Registry di Donato in corso...\n")

try:
    # Cerca TUTTI i modelli registrati
    modelli_registrati = client.search_registered_models()
    
    if not modelli_registrati:
        print("❌ ALLARME ROSSO: Il Model Registry è VUOTO!")
        print("Pracella ha fatto gli 'Experiments', ma non ha 'Registrato' i modelli finali.")
    else:
        for modello in modelli_registrati:
            print(f"📦 Trovato Modello Ufficiale: '{modello.name}'")
            # Cerca le versioni di questo modello
            for versione in modello.latest_versions:
                print(f"   ┣━ Versione: {versione.version}")
                print(f"   ┣━ Stage: {versione.current_stage}")
                print(f"   ┗━ Alias disponibili: {versione.aliases if versione.aliases else 'NESSUN ALIAS!'}")
            print("-" * 40)

except Exception as e:
    print(f"Errore durante la scansione: {e}")