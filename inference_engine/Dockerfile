# Usiamo l'immagine ufficiale e super-ottimizzata di RStudio per Plumber
FROM rstudio/plumber:latest

# Copiamo il nostro script API nel container
COPY api.R /app/api.R

# Impostiamo la cartella di lavoro
WORKDIR /app

# Esponiamo la porta 8000
EXPOSE 8000

# Comando per avviare il server Plumber
CMD ["/app/api.R"]