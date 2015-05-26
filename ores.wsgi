#!/usr/bin/env python3
import os

from flask import request

import yamlconf
from ores.wsgi import application as ores_app

directory = os.path.dirname(os.path.realpath(__file__))

config_path = os.path.join(directory, "config/ores.yaml")

config = yamlconf.load(open(config_path))

application = ores_app.configure(config)
application.debug = True


if __name__ == '__main__':
    application.run(host="0.0.0.0", debug = True)
