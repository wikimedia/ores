"""
Runs a WSGI-based web server that hosts ORES.

Usage:
    wsgi (-h | --help)
    wsgi [--host=<name>] [--port=<num>] [--config-dir=<path>]...
         [--processes=<num>] [--debug] [--verbose] [--logging-config=<path>]

Options:
    -h --help                Print this documentation
    --host=<name>            The hostname to listen on [default: 0.0.0.0]
    --port=<num>             The port number to start the server on
                             [default: 8080]
    --config-dir=<path>      The path to a directory containing configuration
                             [default: config/]
    --logging-config=<path>  The path to a logging configuration file
    --processes=<num>        The number of parallel processes to handle
                             [default: 16]
    --debug                  Print debug logging information
    --verbose                Print verbose extraction information
"""
import logging

import docopt
from ores.wsgi import server
from ores import ores

from .util import build_config

# This is a hack to help know when the models must or must not be loaded
# into memory.  By setting this to True, ClientScoringContext will be used
# rather than ScoringContext
ores._is_wsgi_client = True


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    host = args['--host']
    port = int(args['--port'])
    processes = int(args['--processes'])
    verbose = args['--verbose']
    debug = args['--debug']

    run(host, port, processes, verbose, debug,
        config_dirs=args['--config-dir'],
        logging_config=args['--logging-config'])


def run(host, port, processes, verbose, debug, **kwargs):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    logging.getLogger('requests').setLevel(logging.INFO)
    if verbose:
        logging.getLogger('revscoring.dependencies.dependent') \
               .setLevel(logging.DEBUG)
    else:
        logging.getLogger('revscoring.dependencies.dependent') \
               .setLevel(logging.INFO)

    logging.getLogger("ores.metrics_collectors.logger").setLevel(logging.DEBUG)

    application = build(**kwargs)
    application.debug = True
    application.run(host=host, port=port, processes=processes, debug=True)


def build(*args, **kwargs):
    config = build_config(*args, **kwargs)
    return server.configure(config)
