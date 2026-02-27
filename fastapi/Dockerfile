# 1. Partiamo da un'immagine di Python leggera
FROM python:3.10-slim

# 2. Creiamo una cartella di lavoro dentro il container
WORKDIR /app

# 3. Copiamo la lista delle librerie e le installiamo
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copiamo il nostro codice FastAPI
COPY main.py .

# 5. Il comando per accendere il server (nota lo 0.0.0.0 per esporlo all'esterno)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]