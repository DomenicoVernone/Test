import mlflow
from mlflow.tracking import MlflowClient
import os

# --- 1. CONFIGURAZIONE DAGSHUB ---
DAGSHUB_USER = "carlosto033"        
DAGSHUB_TOKEN = "c51e647b17ed4364332eaba8a4822ae34511fcee"          
REPO_OWNER = "donatooooooo"     
REPO_NAME = "FTD_diagnosis"      

os.environ["MLFLOW_TRACKING_USERNAME"] = DAGSHUB_USER
os.environ["MLFLOW_TRACKING_PASSWORD"] = DAGSHUB_TOKEN

tracking_uri = f"https://dagshub.com/{REPO_OWNER}/{REPO_NAME}.mlflow"
mlflow.set_tracking_uri(tracking_uri)

client = MlflowClient()

# --- 2. I DATI DELLA RUN CHE ABBIAMO SCELTO ---
run_id = "c6dd2232b1444cc4b3308766d7bd28a2" 
model_name = "HC_vs_nfvPPA"
artifact_path = "model" 

print(f"Connessione a: {tracking_uri}")
print(f"Avvio registrazione per il modello: {model_name}...")

# 3. Crea il contenitore nel Registro (Gestione Errori REALE)
try:
    client.create_registered_model(model_name)
    print(f"Creato nuovo slot '{model_name}' nel Model Registry.")
except Exception as e:
    if "RESOURCE_ALREADY_EXISTS" in str(e):
        print(f"Lo slot '{model_name}' esiste già, procedo...")
    else:
        print(f"ERRORE CRITICO di Connessione/Creazione: {e}")
        print("Controlla che Username, Token e Nome Repo siano ESATTI.")
        exit(1) 

# 4. Collega l'artefatto al Registro
print("Estrazione artefatti e creazione Versione 1...")
try:
    source = f"runs:/{run_id}/{artifact_path}"
    version = client.create_model_version(name=model_name, source=source, run_id=run_id)
    
    # 5. Incoroniamo il Modello!
    print(f"Assegnazione alias 'champion' alla versione {version.version}...")
    client.set_registered_model_alias(name=model_name, alias="champion", version=version.version)
    print("SUCCESSO ASSOLUTO! Modello promosso.")

except Exception as e:
    print(f"ERRORE durante la creazione della versione: {e}")
    print("Controlla che il run_id sia corretto e che l'artifact_path sia 'model'.")