# Dockerfile per il servizio di inferenza basato su R e Plumber
FROM rstudio/plumber:latest

# Installazione delle dipendenze di sistema necessarie per i pacchetti R e Plumber
RUN apt-get update -qq && apt-get install -y \
    libssl-dev \
    libcurl4-gnutls-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Installazione dei pacchetti R necessari per il servizio di inferenza
RUN Rscript -e "install.packages(c('plumber', 'uwot', 'jsonlite', 'caret', 'xgboost'), repos='http://cran.rstudio.com/')"

# Imposta la cartella di lavoro e crea una directory condivisa per i dati
WORKDIR /app 
RUN mkdir -p /shared_data

# Copia il codice del servizio di inferenza nella cartella di lavoro
COPY . /app/

EXPOSE 8000

CMD ["/app/api.R"]