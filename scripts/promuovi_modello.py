# File: scripts/promuovi_modello.py
"""
Tool CLI per promuovere una specifica Run di MLflow al rango di 'champion'.
Il backend FastAPI scaricherà automaticamente il modello con questo alias.

Uso:
  python scripts/promuovi_modello.py --run-id <ID> --model-name <NOME>
"""
import os
import argparse
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv

# Carica le variabili dal file .env (assicurati che .env sia in .gitignore)
load_dotenv()

def promuovi_modello(run_id: str, model_name: str, artifact_path: str = "model"):
    # 1. Lettura sicura delle credenziali
    dagshub_user = os.getenv("DAGSHUB_USER")
    dagshub_token = os.getenv("DAGSHUB_TOKEN")
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")

    if not all([dagshub_user, dagshub_token, repo_owner, repo_name]):
        raise EnvironmentError("🚨 Variabili DagsHub mancanti. Assicurati di aver configurato il file .env.")

    os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_user
    os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token

    tracking_uri = f"https://dagshub.com/{repo_owner}/{repo_name}.mlflow"
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()

    print(f"📡 Connessione a: {tracking_uri}")
    print(f"🚀 Avvio registrazione per il modello: '{model_name}' (Run ID: {run_id})...")

    # 2. Gestione Model Registry
    try:
        client.create_registered_model(model_name)
        print(f"✅ Creato nuovo slot '{model_name}' nel Model Registry.")
    except Exception as e:
        if "RESOURCE_ALREADY_EXISTS" in str(e):
            print(f"ℹ️ Lo slot '{model_name}' esiste già, procedo con l'aggiunta della versione...")
        else:
            print(f"❌ ERRORE CRITICO: {e}")
            exit(1)

    # 3. Creazione Versione e Assegnazione Alias
    try:
        source = f"runs:/{run_id}/{artifact_path}"
        version = client.create_model_version(name=model_name, source=source, run_id=run_id)
        
        print(f"👑 Assegnazione alias 'champion' alla versione {version.version}...")
        client.set_registered_model_alias(name=model_name, alias="champion", version=version.version)
        print("🎉 SUCCESSO! Il modello è ora in produzione.")

    except Exception as e:
        print(f"❌ ERRORE durante la promozione: {e}")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Promuovi un modello MLflow a 'champion'.")
    parser.add_argument("--run-id", required=True, help="L'ID della run da promuovere (es. c6dd2232...)")
    parser.add_argument("--model-name", required=True, help="Il nome del modello (es. HC_vs_nfvPPA)")
    parser.add_argument("--artifact-path", default="model", help="Il path dell'artefatto (default: 'model')")
    
    args = parser.parse_args()
    promuovi_modello(args.run_id, args.model_name, args.artifact_path)