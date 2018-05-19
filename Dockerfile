FROM python:3.5-slim

RUN apt-get update && apt-get install -y \
    g++ \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    python3-dev \
    enchant \
    build-essential

COPY . /ores
WORKDIR /ores

RUN pip install pip --upgrade
RUN pip install wheel
RUN pip install nltk
RUN pip install -r /ores/requirements.txt
RUN pip install -r /ores/test-requirements.txt
RUN pip install codecov pytest-cov
RUN python -m nltk.downloader stopwords

EXPOSE 8080
