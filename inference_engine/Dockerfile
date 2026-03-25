# File: inference_engine/Dockerfile
#
# Immagine basata su rstudio/plumber. Il tag 'latest' e' non deterministico:
# per build riproducibili in produzione sostituirlo con un digest specifico.

FROM rstudio/plumber:latest

RUN apt-get update -qq && apt-get install -y \
    libssl-dev \
    libcurl4-gnutls-dev \
    libxml2-dev \
    && rm -rf /var/lib/apt/lists/*

# Mirror CRAN ufficiale con HTTPS e bilanciamento geografico
RUN Rscript -e "install.packages(c('plumber', 'uwot', 'jsonlite', 'caret', 'xgboost'), repos='https://cloud.r-project.org/')"

WORKDIR /app
RUN mkdir -p /shared_data

COPY . /app/

EXPOSE 8000

CMD ["/app/api.R"]