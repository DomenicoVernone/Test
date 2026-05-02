FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    python3-dev \
    git \
    procps \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel

# install dependencies in correct order
RUN pip install numpy==1.23.5

RUN pip install \
    SimpleITK \
    PyWavelets \
    pykwalify

# install pyradiomics WITHOUT build isolation
RUN pip install --no-build-isolation pyradiomics==3.0.1