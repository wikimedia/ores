"""
Runs a pre-caching server against an ORES instance by listening to an RCStream
and submitting requests for scores to the web interface for each revision as it
happens.

If ran by systemd, it uses watchdog to stay alive.

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
                     [default: config]
    --verbose        Print debugging information
"""
import concurrent.futures
import glob
import logging
import os
import sys
import time
from collections import defaultdict

import docopt
import requests
import socketIO_client
import yamlconf

from .watchdog import notify_socket, watchdog_ping

logger = logging.getLogger(__name__)

AVAILABLE_EVENTS = {'edit', 'nonbot_edit'}


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    stream_url = args['<stream-url>']
    ores_url = args['<ores-url>']
    config_paths = os.path.join(args['--config'], "*.yaml")
    config = yamlconf.load(*(open(p) for p in
                             sorted(glob.glob(config_paths))))
    delay = float(args['--delay'])
    verbose = bool(args['--verbose'])
    notify = notify_socket()
    run(stream_url, ores_url, config, delay,
        notify, verbose)


def run(stream_url, ores_url, config, delay, notify, verbose):

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

    if not notify:
        logger.info('Not being ran as a service, watchdog disabled')
    # Build a mapping of wikis and models from the configuration
    score_on = defaultdict(list)
    sp_name = config['ores']['score_processor']
    for context in config['score_processors'][sp_name]['scoring_contexts']:
        for model in config['scoring_contexts'][context].get('precache', []):
            precached_config = \
                config['scoring_contexts'][context]['precache'][model]

            events = precached_config['on']
            if len(set(events) - AVAILABLE_EVENTS) > 0:
                logger.error("{0} events are not available"
                             .format(set(events) - AVAILABLE_EVENTS))
                sys.exit(1)
            for event in precached_config['on']:
                score_on[(event, context)].append(model)
                logger.debug("Setting up precaching for {0} in {1} on {2}"
                             .format(model, context, event))

    def get_score(wiki, model, rev_id):
        url = ores_url + "/scores/" + wiki + "/" + model + \
              "/" + str(rev_id) + "/?precache=true"
        try:
            time.sleep(delay)
            start = time.time()
            requests.get(url, timeout=20, verify=True)
            logger.debug("GET {0} completed in {1} seconds."
                         .format(url, time.time() - start))
            if notify:
                watchdog_ping(*notify)
        except Exception as e:
            logger.error(str(type(e)) + ": " + str(e))

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        class WikiNamespace(socketIO_client.BaseNamespace):
            def on_change(self, change):
                if change['type'] in ('new', 'edit'):
                    wikidb = change['wiki']
                    rev_id = change['revision']['new']
                    for model in score_on[('edit', wikidb)]:
                        executor.submit(get_score, wikidb, model, rev_id)

                    if not change.get('bot'):
                        for model in score_on[('nonbot_edit', wikidb)]:
                            executor.submit(get_score, wikidb, model, rev_id)

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
