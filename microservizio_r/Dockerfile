# 1. Usiamo l'immagine ufficiale
FROM rstudio/plumber:latest

# 2. Creiamo la cartella di lavoro
WORKDIR /app

# 3. Copiamo il nostro script R
COPY plumber.R .

# 4. Diciamo all'immagine semplicemente DOVE si trova il file da lanciare
CMD ["/app/plumber.R"]