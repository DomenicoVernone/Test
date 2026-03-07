# File: inference_engine/Dockerfile

# Usiamo l'immagine ufficiale di RStudio per Plumber
FROM rstudio/plumber:latest

# 1. Installiamo le dipendenze di sistema necessarie per compilare i pacchetti R (httr, uwot)
RUN apt-get update -qq && apt-get install -y \
    libssl-dev \
    libcurl4-gnutls-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Installiamo i pacchetti R necessari per il Clinical Twin
RUN Rscript -e "install.packages(c('plumber', 'uwot', 'jsonlite', 'caret', 'xgboost'), repos='http://cran.rstudio.com/')"
# 3. Creiamo la directory di lavoro e quella per il volume condiviso
WORKDIR /app
RUN mkdir -p /shared_data

# 4. Copiamo il nostro script API nel container
COPY api.R /app/api.R

# 5. Esponiamo la porta 8000
EXPOSE 8000

# 6. Comando per avviare il server Plumber
CMD ["/app/api.R"]