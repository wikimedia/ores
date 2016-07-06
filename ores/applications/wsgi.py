"""
Runs a uwsgi server.

Usage:
    wsgi [--config-dir=<path>]... [--logging-config=<path>]

Options:
    -h --help                Prints this documentation
    --config-dir=<path>      The path to a directory containing configuration
                             [default: config/]
    --logging-config=<path>  The path to a logging configuration file
"""
import logging

import docopt
from ores.wsgi import server
from ores import ores

from .util import build_config

# This is a hack to help know when the models must or must not be loaded
# into memory.
ores._is_wsgi_client = True


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    run(config_dirs=args['--config-dir'],
        logging_config=args['--logging-config'])


def run(*args, **kwargs):
    application = build(*args, **kwargs)
    logging.getLogger('ores').setLevel(logging.DEBUG)
    application.debug = True
    application.run(host="0.0.0.0", processes=16, debug=True)


def build(*args, **kwargs):
    config = build_config(*args, **kwargs)
    return server.configure(config)
