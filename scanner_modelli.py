import os
import mlflow
from mlflow.tracking import MlflowClient

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
experiment_name = "HC_vs_nfvPPA" 

print(f"📡 Connessione a DagsHub per '{experiment_name}'...")

try:
    experiment = client.get_experiment_by_name(experiment_name)
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], max_results=1000)
    
    all_runs_info = []
    print(f"🕵️‍♂️ Trovate {len(runs)} run totali. Inizio analisi completa... attendere...")

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
            artifacts = client.list_artifacts(run_id)
            
        rds_size_kb = 0
        has_valid_rds = False
        
        for f in artifacts:
            if f.path.endswith(".rds"):
                rds_size_kb = round(f.file_size / 1024, 2)
                if f.file_size > 1000: # Maggiore di 1KB
                    has_valid_rds = True
                break # Trovato il file rds, possiamo uscire dal ciclo degli artefatti
                
        # Valutazione dello STATUS
        if "xgboost" in source_file:
            status = "❌ XGBoost (No UMAP)"
        elif not has_valid_rds:
            status = f"❌ File vuoto ({rds_size_kb}KB)"
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

    # Ordiniamo per AUC decrescente, così vediamo subito chi era in cima e perché è stato scartato
    all_runs_info.sort(key=lambda x: x["auc"], reverse=True)

    # --- STAMPA DELLA TABELLA ---
    print("\n" + "="*115)
    print(f"{'RUN ID':<35} | {'SOURCE':<15} | {'SIZE(KB)':<8} | {'AUC':<7} | {'SENS':<7} | {'SPEC':<7} | {'STATUS'}")
    print("="*115)
    
    for v in all_runs_info:
        print(f"{v['run_id']:<35} | {v['source']:<15} | {v['size_kb']:<8} | {v['auc']:.4f} | {v['sens']:.4f} | {v['spec']:.4f} | {v['status']}")
    
    print("="*115)
    print("✅ Scansione completata con successo. Tutte le run sono state tracciate.")

except Exception as e:
    print(f"🚨 Errore: {e}")