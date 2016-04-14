"""
Starts a development web server.

Usage:
    dev_server (-h | --help)
    dev_server [--host=<name>] [--port=<num>] [--config=<path>]
               [--processes=<num>] [--debug] [--verbose]

Options:
    -h --help          Print this documentation
    --host=<name>      The hostname to listen on [default: 0.0.0.0]
    --port=<num>       The port number to start the server on [default: 8080]
    --config=<path>    The path to a yaml config file
                       [default: config]
    --processes=<num>  The number of parallel processes to handle [default: 32]
    --debug            Print debug logging information
    --verbose          Print verbose extraction information
"""
import docopt
import glob
import logging
import os
import yamlconf

from ..wsgi import server


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    config_paths = os.path.join(args['--config'], "*.yaml")
    config = yamlconf.load(*(open(p) for p in
                             sorted(glob.glob(config_paths))))

    processes = int(args['--processes'])

    verbose = args['--verbose']

    debug = args['--debug']

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

    app = server.configure(config)
    app.run(host=args['--host'],
            port=int(args['--port']),
            debug=True,
            processes=processes)
