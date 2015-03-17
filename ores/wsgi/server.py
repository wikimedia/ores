"""
WSGI Server

Starts a web server for hosting access to a set of scorers.

Usage:
    server (-h | --help)
    server [--port=<num>] [--verbose] <enwiki_reverts> <ptwiki_reverts>

Options:
    -h --help        Print this documentation
    --port=<num>     The port number to start the server on [default: 8080]
    --verbose        Print logging information
"""
import docopt

from . import routes, scorers
from .app import app


def main():
    args = docopt.docopt(__doc__)

    scorers.configure(
        open(args['<enwiki_reverts>'], 'rb'),
        open(args['<ptwiki_reverts>'], 'rb'),
        'https://en.wikipedia.org/w/api.php',
        'https://pt.wikipedia.org/w/api.php'
    )

    app.run(
        host="0.0.0.0",
        port=int(args['--port']),
        debug=True
    )
