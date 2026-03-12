SHELL = /bin/bash

ifeq ($(OS),Windows_NT)
        ACTIVATE := venv\Scripts\activate
    else
        ACTIVATE := source venv/bin/activate
    endif

.ONESHELL:

git_init:
	git init
	git add .
	git commit -m "Initial commit"

dvc_init:
	dvc init
	git add .
	git commit -m "Initialize DVC"

tracking:
	@echo "Start MLflow tracking..."
	mlflow server --host 127.0.0.1 --port 8080 --backend-store-uri src/models/mlruns

static_analysis:
	@echo "Start static_analysis checks..."
	echo "Executing Ruff..." && ruff check als_diagnosis
	echo "Executing Mypy..." && mypy als_diagnosis
	echo "Executing Bandit..." && bandit -r als_diagnosis

tests:
	@echo "Start testing..."
	pytest tests/