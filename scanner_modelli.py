import os
import mlflow
from mlflow.tracking import MlflowClient

# --- 1. CONFIGURAZIONE DAGSHUB ---
DAGSHUB_USER = "carlosto033"        # Es: carlo...
DAGSHUB_TOKEN = "c51e647b17ed4364332eaba8a4822ae34511fcee"          
REPO_OWNER = "donatooooooo"     
REPO_NAME = "FTD_diagnosis"        

os.environ["MLFLOW_TRACKING_USERNAME"] = DAGSHUB_USER
os.environ["MLFLOW_TRACKING_PASSWORD"] = DAGSHUB_TOKEN
tracking_uri = f"https://dagshub.com/{REPO_OWNER}/{REPO_NAME}.mlflow"
mlflow.set_tracking_uri(tracking_uri)

client = MlflowClient()

# --- 2. NOME DELL'ESPERIMENTO ---
experiment_name = "HC_vs_nfvPPA" 

print(f"📡 Connessione a DagsHub...")
print(f"🔍 Scansione '{experiment_name}' con rilevamento algoritmo (No XGBoost)...\n")

try:
    experiment = client.get_experiment_by_name(experiment_name)
    if not experiment:
        print(f"🚨 Esperimento '{experiment_name}' non trovato!")
        exit(1)
        
    runs = client.search_runs(experiment_ids=[experiment.experiment_id])
    valid_runs = []

    for run in runs:
        run_id = run.info.run_id
        
        # MAGIA: Recupera il nome del file R usato per il training (es. XGBoost.R, random_forest.R)
        source_tag = run.data.tags.get("mlflow.source.name", "Sconosciuto")
        source_file = os.path.basename(source_tag).lower()
        
        try:
            artifacts = client.list_artifacts(run_id, path="model")
        except:
            artifacts = client.list_artifacts(run_id)
            
        for f in artifacts:
            if f.path.endswith(".rds"):
                if f.file_size > 1000: 
                    
                    auc = run.data.metrics.get("auc", 0)
                    acc = run.data.metrics.get("accuracy", 0)
                    sens = run.data.metrics.get("sensitivity", 0)
                    spec = run.data.metrics.get("specificity", 0)
                    
                    valid_runs.append({
                        "run_id": run_id,
                        "source": source_file,
                        "size_kb": round(f.file_size / 1024, 2),
                        "auc": auc,
                        "acc": acc,
                        "sens": sens,
                        "spec": spec
                    })

    # Ordiniamo per AUC decrescente
    valid_runs.sort(key=lambda x: x["auc"], reverse=True)

    print("-" * 110)
    print(f"{'RUN ID':<35} | {'SOURCE':<15} | {'SIZE(KB)':<8} | {'AUC':<7} | {'ACC':<7} | {'SENS':<7} | {'SPEC':<7}")
    print("-" * 110)
    
    # Stampiamo i Top 10
    for v in valid_runs[:10]:
        # Flag visivo anti-XGBoost
        if "xgboost" in v["source"]:
            status = "❌ SCARTA (XGBoost)"
        else:
            status = "✅ OK (Candidato)"
            
        print(f"{v['run_id']:<35} | {v['source']:<15} | {v['size_kb']:<8} | {v['auc']:.4f} | {v['acc']:.4f} | {v['sens']:.4f} | {v['spec']:.4f} | {status}")
    
    if not valid_runs:
        print("❌ NESSUN MODELLO VALIDO TROVATO!")

except Exception as e:
    print(f"🚨 Errore durante la scansione: {e}")