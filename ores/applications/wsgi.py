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
    --processes=<num>        The number of parallel processes to handle
                             [default: 16]
    --debug                  Print debug logging information
    --verbose                Print verbose extraction information
"""
import docopt

from ores import ores
from ores.wsgi import server

from .util import build_config, configure_logging

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

    run(host, port, processes,
        verbose=verbose, debug=debug,
        config_dirs=args['--config-dir'])


def run(host, port, processes, **kwargs):
    application = build(**kwargs)
    application.debug = True
    application.run(host=host, port=port, processes=processes, threaded=False, debug=True)


def build(**kwargs):
    config = build_config(**kwargs)
    configure_logging(config=config, **kwargs)
    return server.configure(config)
