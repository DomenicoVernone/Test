import mlflow

with mlflow.start_run() as run:

    mlflow.log_artifact("model.rds", artifact_path="model")

    mlflow.register_model(
        model_uri=f"runs:/{run.info.run_id}/model",
        name="Model.Rds"
    )

print("Model registered successfully")
