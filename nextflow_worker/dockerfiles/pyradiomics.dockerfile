FROM python:3.12.9-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=en_US.UTF-8
ENV LANGUAGE=en_US:en
ENV LC_ALL=en_US.UTF-8

RUN apt update -y && \
    apt upgrade -y && \
    apt install -y --no-install-recommends \
        locales \
        wget \
        unzip \
        file \
        dc \
        mesa-utils \
        libquadmath0 \
        libgomp1 \
        bzip2 \
        ca-certificates \
        curl \
        build-essential \
        cmake && \
    echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    bash miniconda.sh -b -p /opt/conda && \
    rm miniconda.sh

ENV PATH="/opt/conda/bin:${PATH}"

RUN wget https://github.com/AIM-Harvard/pyradiomics/archive/refs/heads/master.zip && \
    unzip master.zip && \
    cd pyradiomics-master && \
    python -m pip install . && \
    cd .. && \
    rm -rf pyradiomics-master master.zip

COPY requirements.txt .

RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

CMD [ "bash" ]
