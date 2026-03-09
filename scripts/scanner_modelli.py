# File: scripts/scanner_modelli.py
"""
Tool CLI per scansionare e valutare le run di un determinato esperimento su DagsHub/MLflow.
Restituisce una tabella comparativa per decidere quale run promuovere.

Uso:
  python scripts/scanner_modelli.py --experiment-name HC_vs_nfvPPA
"""
import os
import argparse
import mlflow
from mlflow.tracking import MlflowClient
from dotenv import load_dotenv

load_dotenv()

def scansiona_esperimento(experiment_name: str):
    # 1. Lettura sicura credenziali
    dagshub_user = os.getenv("DAGSHUB_USER")
    dagshub_token = os.getenv("DAGSHUB_TOKEN")
    repo_owner = os.getenv("REPO_OWNER")
    repo_name = os.getenv("REPO_NAME")

    if not all([dagshub_user, dagshub_token, repo_owner, repo_name]):
        raise EnvironmentError("🚨 Variabili DagsHub mancanti nel file .env.")

    os.environ["MLFLOW_TRACKING_USERNAME"] = dagshub_user
    os.environ["MLFLOW_TRACKING_PASSWORD"] = dagshub_token
    tracking_uri = f"https://dagshub.com/{repo_owner}/{repo_name}.mlflow"
    mlflow.set_tracking_uri(tracking_uri)

    client = MlflowClient()

    print(f"📡 Connessione a DagsHub per l'esperimento '{experiment_name}'...")

    try:
        experiment = client.get_experiment_by_name(experiment_name)
        if not experiment:
            print(f"❌ Errore: Nessun esperimento trovato con il nome '{experiment_name}'.")
            exit(1)

        runs = client.search_runs(experiment_ids=[experiment.experiment_id], max_results=1000)
        
        all_runs_info = []
        print(f"🕵️‍♂️ Trovate {len(runs)} run totali. Inizio ispezione artefatti...")

        for run in runs:
            run_id = run.info.run_id
            source_tag = run.data.tags.get("mlflow.source.name", "Sconosciuto")
            source_file = os.path.basename(source_tag).lower()
            
            auc = run.data.metrics.get("auc", 0)
            sens = run.data.metrics.get("sensitivity", 0)
            spec = run.data.metrics.get("specificity", 0)
            
            # Ispezione degli artefatti
            try:
                artifacts = client.list_artifacts(run_id, path="model")
            except:
                try:
                    artifacts = client.list_artifacts(run_id)
                except:
                    artifacts = []
                
            rds_size_kb = 0
            has_valid_rds = False
            
            for f in artifacts:
                if f.path.endswith(".rds"):
                    rds_size_kb = round(f.file_size / 1024, 2)
                    if f.file_size > 1000: # Maggiore di 1KB
                        has_valid_rds = True
                    break 
                    
            # Valutazione
            if "xgboost" in source_file:
                status = "❌ XGBoost (No UMAP)"
            elif not has_valid_rds:
                status = f"❌ RDS non valido ({rds_size_kb}KB)"
            else:
                status = "✅ OK"
                
            all_runs_info.append({
                "run_id": run_id,
                "source": source_file,
                "size_kb": rds_size_kb,
                "auc": auc,
                "sens": sens,
                "spec": spec,
                "status": status
            })

        # Ordiniamo per AUC
        all_runs_info.sort(key=lambda x: x["auc"], reverse=True)

        print("\n" + "="*115)
        print(f"{'RUN ID':<35} | {'SOURCE':<15} | {'SIZE(KB)':<8} | {'AUC':<7} | {'SENS':<7} | {'SPEC':<7} | {'STATUS'}")
        print("="*115)
        
        for v in all_runs_info:
            print(f"{v['run_id']:<35} | {v['source']:<15} | {v['size_kb']:<8} | {v['auc']:.4f} | {v['sens']:.4f} | {v['spec']:.4f} | {v['status']}")
        
        print("="*115)
        print("✅ Scansione completata.")

    except Exception as e:
        print(f"🚨 Errore critico: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scansiona le run di un esperimento MLflow.")
    parser.add_argument("--experiment-name", required=True, help="Nome dell'esperimento MLflow (es. HC_vs_nfvPPA)")
    
    args = parser.parse_args()
    scansiona_esperimento(args.experiment_name)