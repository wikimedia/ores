#!/usr/bin/env python3
import logging
import os

from flask import request

import yamlconf
from ores.wsgi import server

directory = os.path.dirname(os.path.realpath(__file__))

config_path = os.path.join(directory, "config/ores.yaml")

config = yamlconf.load(open(config_path))

application = server.configure(config)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    application.debug = True
    application.run(host="0.0.0.0", debug = True)
