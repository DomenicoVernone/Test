FROM rocker/tidyverse:4.1

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/mlflow-venv && \
    /opt/mlflow-venv/bin/pip install --upgrade pip && \
    /opt/mlflow-venv/bin/pip install mlflow

ENV MLFLOW_PYTHON_BIN=/opt/mlflow-venv/bin/python
ENV MLFLOW_BIN=/opt/mlflow-venv/bin/mlflow
ENV PATH="/opt/mlflow-venv/bin:${PATH}"

RUN R -e "install.packages('mlflow')"

RUN R -e "install.packages(c('cvTools', 'glmnet', 'caret', 'plotmo', 'BBmisc', \
    'e1071', 'ROCit', 'randomForest', 'dplyr', 'xgboost', 'tidyverse', 'mlr', 'knitr'), \
    repos='http://cran.rstudio.com/')"

RUN R -e "install.packages('imbalance')"

WORKDIR /app
COPY . .

CMD ["bash"]