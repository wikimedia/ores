[![Build Status](https://travis-ci.org/wikimedia/ores.svg)](https://travis-ci.org/wikimedia/ores)
[![Test coverage](https://codecov.io/gh/wikimedia/ores/branch/master/graph/badge.svg)](https://codecov.io/gh/wikimedia/ores)
[![GitHub license](https://img.shields.io/github/license/wikimedia/ores.svg)](./LICENSE)
[![PyPI version](https://badge.fury.io/py/ores.svg)](https://badge.fury.io/py/ores)

ORES
====

<blockquote>
⚠️ Warning: As of late 2023, the ORES infrastructure is being deprecated by the
WMF Machine Learning team, please check https://wikitech.wikimedia.org/wiki/ORES for more info.

While the code in this repository may still work, it is unmaintained, and as
such may break at any time. Special consideration should also be given to
machine learning models seeing drift in quality of predictions.

The replacement for ORES and associated infrastructure is Lift Wing:
https://wikitech.wikimedia.org/wiki/Machine_Learning/LiftWing

Some Revscoring models from ORES run on the Lift Wing infrastructure, but they
are otherwise unsupported (no new training or code updates).

They can be downloaded from the links documented at:
https://wikitech.wikimedia.org/wiki/Machine_Learning/LiftWing#Revscoring_models_(migrated_from_ORES)

In the long term, some or all these models *may* be replaced by newer models
specifically tailored to be run on modern ML infrastructure like Lift Wing.

If you have any questions, contact the WMF Machine Learning team:
https://wikitech.wikimedia.org/wiki/Machine_Learning
</blockquote>

A webserver for hosting scoring services. For more information, see [the ORES documentation on MediaWiki](https://mediawiki.org/wiki/ORES).

Installation
============
ORES is based on Python 3. Use pip to install ORES:

``pip install ores`` (or ``pip3 install ores`` if your distribution defaults to Python 2)

If you're running with the default Redis configuration, you'll need to install a few more optional libraries,

``pip install ores[redis]``

Then you can easily run a test server by:

``ores applications.wsgi``

Use the ``-h`` argument to view its usage.

``ores applications.wsgi -h``

Visit these pages to see if your installation works,

``http://localhost:8080/``
``http://localhost:8080/v2/scores/testwiki/revid/641962088?features=true``

Running ores using docker composer
==================================
As an easy way to run ores for development, download and install [docker-compose](https://docs.docker.com/compose/) and then do:

``docker-compose build && docker-compose up``

ores will be accessible through localhost:8080

Running tests
=============
For a native installation, make sure you installed dependencies for testing:

``pip install -r test-requirements.txt``

then run:

``py.test .``

For docker installation, run:

``docker-compose exec ores-worker py.test /ores``

Utilities
=========
ORES provides several utilities:
* `precached`: Starts a daemon that requests scores for revisions as they happen
* `score_revisions`: Scores a set of revisions using an ORES API
* `stress_test`: Scores a large set of revisions at a configurable rate
* `test_api`: Runs a series of tests against a live ORES API

In order to run any of them, run it through `./utility` wrapper:

``./utility test_api -h``

For docker installations run it through one of containers:

``docker-compose exec ores-worker /ores/utility test_api -h``

Authors
=======
* [Aaron Halfaker](https://github.com/halfak)
* [Yuvi Panda](https://github.com/yuvipanda)
* [Amir Sarabadani](https://github.com/Ladsgroup)
* [Justin Du](https://github.com/mdew192837)
* [Adam Wight](https://github.com/adamwight)
