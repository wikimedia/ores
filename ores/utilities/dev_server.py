"""
Starts a development web server.

Usage:
    dev_server (-h | --help)
    dev_server [--host=<name>] [--port=<num>] [--config=<path>]
               [--processes=<num>] [--verbose]

Options:
    -h --help          Print this documentation
    --host=<name>      The hostname to listen on [default: 0.0.0.0]
    --port=<num>       The port number to start the server on [default: 8080]
    --config=<path>    The path to a yaml config file
                       [default: config/ores-testwiki.yaml]
    --processes=<num>  The number of parallel processes to handle [default: 32]
    --verbose          Print logging information
"""
import logging

import docopt
import yamlconf

from ..wsgi import server


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    config = yamlconf.load(open(args['--config']))

    processes = int(args['--processes'])

    logging.basicConfig(
        level=logging.INFO if not args['--verbose'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )

    logging.getLogger("ores.metrics_collectors.logger").setLevel(logging.DEBUG)

    app = server.configure(config)
    app.run(host=args['--host'],
            port=int(args['--port']),
            debug=True,
            processes=processes)
