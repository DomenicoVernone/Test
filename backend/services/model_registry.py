"""
Model Selection Service.
Si interfaccia con l'MLflow Model Registry (su DagsHub) di Donato 
per estrarre dinamicamente l'artefatto (.rds) del modello 'Champion'
in base alla variante FTD selezionata dal medico.
"""
import os
import mlflow
from mlflow.tracking import MlflowClient

# Coordinate del Repository DagsHub di Donato
DAGSHUB_REPO_OWNER = "donatooooooo"
DAGSHUB_REPO_NAME = "FTD_diagnosis"
MLFLOW_TRACKING_URI = f"https://dagshub.com/{DAGSHUB_REPO_OWNER}/{DAGSHUB_REPO_NAME}.mlflow"

def download_champion_model(model_name: str, download_dir: str):
    """
    Cerca su MLflow il modello specificato e scarica SOLO la versione 
    che ha l'alias 'Champion' (il Best Model).
    """
    try:
        # 1. Recupera le credenziali corrette dal .env
        dagshub_user = os.environ.get("DAGSHUB_USERNAME")
        dagshub_token = os.environ.get("MLFLOW_TRACKING_PASSWORD")

        if not dagshub_user or not dagshub_token:
            print("⚠️ [Model Registry] Errore: Credenziali DagsHub mancanti nel file .env.")
            return None

        # Imposta username e password ESATTI per MLflow
        os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_user
        os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token
        
        # 2. Connessione a MLflow (puntando sempre al repo di Donato)
        mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
        client = MlflowClient()

        print(f"🔍 [Model Selection] Ricerca del modello '{model_name}' con alias 'Champion'...")

        # 3. Interroga MLflow per trovare la versione "Champion"
        champion_version = client.get_model_version_by_alias(name=model_name, alias="Champion")
        
        print(f"✅ [Model Selection] Trovata versione {champion_version.version} (Alias: Champion). Download artefatto in corso...")

        # 4. Download fisico del file (.rds) nel Volume Condiviso
        os.makedirs(download_dir, exist_ok=True)
        
        # MLflow format per scaricare un modello tramite alias
        model_uri = f"models:/{model_name}@Champion"
        
        local_path = mlflow.artifacts.download_artifacts(
            artifact_uri=model_uri,
            dst_path=download_dir
        )
        
        print(f"🎉 [Model Selection] Modello 'Champion' scaricato in: {local_path}")
        return local_path

    except mlflow.exceptions.RestException as e:
        print(f"❌ [Model Selection] Modello '{model_name}' o alias 'Champion' non trovato su DagsHub. Dettagli: {e}")
        return None
    except Exception as e:
        print(f"🚨 [Model Selection] Errore di connessione: {e}")
        return None