# File: backend/Dockerfile
# Usa l'immagine ufficiale di Python
FROM python:3.10-slim

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