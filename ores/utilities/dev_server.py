"""
Starts a development web server.

Usage:
    wsgi_server (-h | --help)
    wsgi_server [--port=<num>] [--verbose] [--config=<path>]

Options:
    -h --help        Print this documentation
    --port=<num>     The port number to start the server on [default: 8080]
    --config=<path>  The path to a yaml config file
    --verbose        Print logging information
"""
import docopt

import yamlconf

from ..wsgi import application


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    if args['--config'] is not None:
        config = yamlconf.load(open(args['--config']))
    else:
        config = None

    app = application.configure(config)
    app.run(host="0.0.0.0",
            port=int(args['--port']),
            debug=True)
