FROM python:3.7-slim-stretch

RUN apt-get update && apt-get install -y \
    g++ \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    enchant \
    build-essential
COPY requirements.txt /ores/requirements.txt
COPY test-requirements.txt /ores/test-requirements.txt
RUN pip install pip --upgrade && pip install wheel && pip install nltk \
    && pip install -r /ores/requirements.txt \
    && pip install -r /ores/test-requirements.txt \
    && python -m nltk.downloader stopwords

COPY . /ores
WORKDIR /ores

EXPOSE 8080
