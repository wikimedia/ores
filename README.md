[![Build Status](https://travis-ci.org/wiki-ai/ores.svg)](https://travis-ci.org/wiki-ai/ores)

Objective Revision Evaluation Service
=====================================
A webserver for hosting scoring services. For more information, see [the ORES documentation on MediaWiki](https://mediawiki.org/wiki/ORES).

Installation
============
ORES is based on Python 3. Use pip to install ORES:

``pip install ores`` (or ``pip3 install ores`` if your distribution defaults to Python 2)

If you're running with the default configuration, you'll need to install a few more optional libraries,

``pip install pylru``

Then you can easily run a test server by:

``ores applications.wsgi``

Use the ``-h`` argument to view its usage.

``ores applications.wsgi -h``

Visit these pages to see if your installation works,

``http://localhost:8080/``
``http://localhost:8080/v2/scores/testwiki/revid/641962088?features=true``

Running a development server
============================
We recommend that you set up a python "virtual environment".  We put together
[this guide](https://gist.github.com/halfak/9f4830895496af9e9731) to help you
get everything set up.  

Install requirements AND the test-requirements in order to run the default
test server and experiment with different scoring strategies.

* `$ pip install -r requirements.txt`
* `$ pip install -r test-requirements.txt`

Run a test server as ORES using the `./utility`, so local changes are
reflected: Use `-h` to view its usage

* `$ ./utility applications.wsgi`

Check if everything is running on `http://localhost:8080`.

Authors
=======
* [Aaron Halfaker](https://github.com/halfak)
* [Yuvi Panda](https://github.com/yuvipanda)
* [Amir Sarabadani](https://github.com/Ladsgroup)
* [Justin Du](https://github.com/mdew192837)
