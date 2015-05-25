#!/usr/bin/env python3
import os

from flask import request

import yamlconf
from ores.wsgi import application

directory = os.path.dirname(os.path.realpath(__file__))

config_path = os.path.join(directory, "config/ores.yaml")

config = yamlconf.load(open(config_path))

app = application.configure(config)
app.debug = True


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug = True)
