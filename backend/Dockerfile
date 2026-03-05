# Usa l'immagine ufficiale di Python
FROM python:3.10-slim

# Imposta la cartella di lavoro dentro il container
WORKDIR /app

# Copia i requirements e installa le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia TUTTO il codice del backend (main.py, core/, models/, routers/, ecc.)
COPY . .

# Il comando di avvio è gestito dal docker-compose.yml, ma lo lasciamo per sicurezza
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]