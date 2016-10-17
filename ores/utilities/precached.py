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

from ..metrics_collectors import MetricsCollector, Null
from .watchdog import notify_socket, watchdog_ping

logger = logging.getLogger(__name__)

AVAILABLE_EVENTS = {'edit', 'nonbot_edit'}
MAX_WORKERS = 50


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
    ss_name = config['ores']['scoring_system']
    if 'metrics_collector' in config['scoring_systems'][ss_name]:
        metrics_collector = MetricsCollector.from_config(
            config, config['scoring_systems'][ss_name]['metrics_collector'])
    else:
        metrics_collector = Null()

    run(stream_url, ores_url, metrics_collector, config, delay,
        notify, verbose)


def run(stream_url, ores_url, metrics_collector, config, delay, notify, verbose):

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
    # If we're using logging for metrics collection, show it.
    logging.getLogger("ores.metrics_collectors").setLevel(logging.DEBUG)

    if not notify:
        logger.info('Not being ran as a service, watchdog disabled')

    score_on = build_score_on(config)
    RCNamespace = build_RCNamespace(
        stream_url, score_on, ores_url, MAX_WORKERS, metrics_collector, delay,
        notify)

    socketIO = socketIO_client.SocketIO(stream_url, 80)
    socketIO.define(RCNamespace, '/rc')

    try:
        socketIO.wait(seconds=sys.maxsize)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.  Shutting down.")
        socketIO.disconnect()


def build_score_on(config):
    # Build a mapping of wikis and models from the configuration
    score_on = defaultdict(list)
    ss_name = config['ores']['scoring_system']
    for context in config['scoring_systems'][ss_name]['scoring_contexts']:
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

    return score_on


def build_RCNamespace(stream_url, score_on, ores_url, max_workers,
                       metrics_collector, delay, notify):

    class _RCNamespace(socketIO_client.BaseNamespace):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            print("RecentChanges.__init__", args, kwargs)
            self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)

        def on_change(self, change):
            if change['type'] in ('new', 'edit'):
                wikidb = change['wiki']
                rev_id = change['revision']['new']
                models = score_on.get(('edit', wikidb), [])
                self.score_revision(wikidb, models, rev_id)

                if not change.get('bot'):
                    models = score_on.get(('nonbot_edit', wikidb), [])
                    self.score_revision(wikidb, models, rev_id)

        def on_connect(self):
            logger.info("Connecting socketIO client to {0}."
                        .format(stream_url))

            # TODO: This should be limited to the wikis we actually care about
            # but we identify a wiki by it's dbname and this pattern matching
            # uses a domain name.
            self.emit('subscribe', '*')  # Subscribes to all wikis

        def on_disconnect(self):
            self.executor.shutdown(wait=False)

        def score_revision(self, context_name, model_names, rev_id):
            self.executor.submit(
                self._score_revision, context_name, model_names, rev_id)

        def _score_revision(self, context_name, model_names, rev_id):
            if not model_names:
                return
            url = ores_url + "/v2/scores/" + context_name + "/" + \
                  "?models=" + "|".join(model_names) + \
                  "&revids=" + str(rev_id) + \
                  "&precache=true"
            try:
                time.sleep(delay)
                start = time.time()
                response = requests.get(url, timeout=20, verify=True)
                if response.status_code == 200:
                    first_model_doc = \
                        response.json()['scores'][context_name][model_names[0]]
                    if 'error' not in first_model_doc['scores'][str(rev_id)]:
                        metrics_collector.precache_score(
                            context_name, model_names, time.time() - start)
                    else:
                        metrics_collector.precache_scoring_error(
                            context_name, model_names, response.status_code,
                            time.time() - start)
                        logger.warning(
                            "Request to {0} failed with {1} response: \n\t{2}"
                            .format(url, response.status_code,
                                    first_model_doc['scores'][str(rev_id)]))

                else:
                    metrics_collector.precache_scoring_error(
                        context_name, model_names, response.status_code,
                        time.time() - start)
                    logger.warning(
                        "Request to {0} failed with {1} response: \n\t{2}"
                        .format(url, response.status_code, response.content[:500]))
                if notify:
                    watchdog_ping(*notify)
            except requests.exceptions.ReadTimeout:
                metrics_collector.precache_scoring_error(
                    context_name, model_names, 504,
                    time.time() - start)
                logger.warning(
                    "Request to {0} timed out in {1} seconds"
                    .format(url, round(time.time() - start, 3)))
            except Exception as e:
                logger.error(str(type(e)) + ": " + str(e))

    return _RCNamespace
