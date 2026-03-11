# File: backend/Dockerfile
# Usa l'immagine ufficiale di Python
FROM python:3.10-slim

# ==========================================
# DIPENDENZE DI SISTEMA: JAVA E NEXTFLOW
# ==========================================
# 1. Installa Java (JRE), curl, unzip e procps (richiesti da Nextflow)

RUN apt-get update && apt-get install -y \ 
    default-jre \
    curl \
    unzip \
    procps \
    && rm -rf /var/lib/apt/lists/*

# 2. Scarica e installa l'eseguibile di Nextflow globalmente
RUN curl -s https://get.nextflow.io | bash && \
    mv nextflow /usr/local/bin/nextflow && \
    chmod +x /usr/local/bin/nextflow
# ==========================================

# Imposta la cartella di lavoro
WORKDIR /app

# Copia i requirements e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia tutto il codice del backend
COPY . .

# Esponiamo esplicitamente la porta (Best Practice per la leggibilità)
EXPOSE 8000

# Comando di avvio (In produzione si userebbero più worker, ma per ora uvicorn base va bene)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]