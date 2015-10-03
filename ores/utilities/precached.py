"""
Runs a pre-caching server against an ORES instance by listening to an RCStream
and submitting requests for scores to the web interface for each revision as it
happens.

:Usage:
    precached -h | --help
    precached <stream-url> <ores-url> [--config=<path>] [--delay=<secs>]
                                      [--verbose]

:Options:
    -h --help        Prints this documentation
    <stream-url>     URL of an RCStream
    <ores-url>       URL of base ORES webserver
    --delay=<secs>   The delay between when an event is received and when the
                     request is sent to ORES. [default: 0]
    --config=<path>  The path to a yaml config file
                     [default: config/ores-localdev.yaml]
    --verbose        Print debugging information
"""
import concurrent.futures
import logging
import sys
import time
from collections import defaultdict

import docopt
import requests
import socketIO_client
import yamlconf

logger = logging.getLogger(__name__)


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    stream_url = args['<stream-url>']
    ores_url = args['<ores-url>']
    config = yamlconf.load(open(args['--config']))
    delay = float(args['--delay'])
    verbose = bool(args['--verbose'])
    run(stream_url, ores_url, config, delay,
        verbose)


def run(stream_url, ores_url, config, delay, verbose):

    if verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )

    # Make requests and socketIO_client be quiet.  They are very noisy.
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("socketIO_client").setLevel(logging.ERROR)  # SHUT UP!
    requests.packages.urllib3.disable_warnings()

    # Build a mapping of wikis and models from the configuration
    wiki_models = defaultdict(list)
    sp_name = config['ores']['score_processor']
    for wiki in config['score_processors'][sp_name]['scoring_contexts']:
        for model in config['scoring_contexts'][wiki]['scorer_models']:
            wiki_models[wiki].append(model)

    def get_score(wiki, model, rev_id):
        url = ores_url + "/scores/" + wiki + "/" + model + \
              "/" + str(rev_id) + "/?precache=true"
        try:
            time.sleep(delay)
            start = time.time()
            requests.get(url, timeout=20, verify=False)
            logger.debug("GET {0} completed in {1} seconds."
                         .format(url, time.time() - start))
        except Exception as e:
            logger.error(str(type(e)) + ": " + str(e))

    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        class WikiNamespace(socketIO_client.BaseNamespace):
            def on_change(self, change):
                if change['type'] in ('new', 'edit'):
                    wiki = change['wiki']
                    rev_id = change['revision']['new']
                    for model in wiki_models[wiki]:
                        start = time.time()
                        executor.submit(get_score, wiki, model, rev_id)
                        logger.debug("GET {0} started in {1} seconds."
                                     .format((wiki, model, rev_id),
                                             time.time() - start))

            def on_connect(self):
                logger.info("Connecting socketIO client to {0}."
                            .format(stream_url))

                # TODO: This should be limited to the wikis we actually care about
                # but we identify a wiki by it's dbname and this pattern matching
                # uses a domain name.
                self.emit('subscribe', '*')  # Subscribes to all wikis

        socketIO = socketIO_client.SocketIO(stream_url, 80)
        socketIO.define(WikiNamespace, '/rc')

        try:
            socketIO.wait(seconds=sys.maxsize)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected.  Shutting down.")
