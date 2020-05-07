FROM docker-registry.wikimedia.org/python3-build-stretch

RUN apt-get update && apt-get install -y \
    g++ \
    gfortran \
    libblas-dev \
    liblapack-dev \
    libopenblas-dev \
    python3-dev \
    python3-pip \
    enchant \
    build-essential

COPY . /ores
WORKDIR /ores

RUN pip3 install pip --upgrade
RUN pip3 install wheel
RUN pip3 install nltk
RUN pip3 install -r /ores/requirements.txt
RUN pip3 install -r /ores/test-requirements.txt
RUN python3 -m nltk.downloader stopwords

EXPOSE 8080
