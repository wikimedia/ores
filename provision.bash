#!/bin/bash

apt-get update
apt-get install -q -y git-core
apt-get install -q -y redis-server
apt-get install -q -y python3-scipy
apt-get install -q -y virtualenv python3-dev build-essential gfortran libopenblas-dev liblapack-dev
apt-get install -q -y enchant
apt-get install -q -y myspell-pt myspell-fa myspell-en-au myspell-en-gb myspell-en-us myspell-en-za myspell-fr myspell-es

mkdir -p /srv/ores/venv
virtualenv --python python3 --system-site-packages /srv/ores/venv

/srv/ores/venv/bin/pip install -r /vagrant/requirements.txt
mkdir -p /usr/local/share/nltk_data
/srv/ores/venv/bin/python -m nltk.downloader -d /usr/local/share/nltk_data wordnet omw stopwords

ln -f -s /vagrant/celery-dev.service /etc/systemd/system
ln -f -s /vagrant/uwsgi-dev.service /etc/systemd/system
systemctl daemon-reload
systemctl start celery-dev uwsgi-dev
