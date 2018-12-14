"""
Runs a pre-caching server against an ORES instance by listening to an
EventStream and submitting requests for scores to the web interface for each
revision as it happens.

:Usage:
    precached -h | --help
    precached <stream-url> <ores-url> [--config=<path>] [--delay=<secs>]
                                      [--debug]

:Options:
    -h --help        Prints this documentation
    <stream-url>     URL of an RCStream
    <ores-url>       URL of base ORES webserver
    --delay=<secs>   The delay between when an event is received and when the
                     request is sent to ORES. [default: 0]
    --config=<path>  The path to a yaml config file
                     [default: config]
    --debug          Print debugging information
"""
import glob
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor

import docopt
import requests
import yamlconf
from sseclient import SSEClient

from ..metrics_collectors import MetricsCollector, Null

logger = logging.getLogger(__name__)

MAX_WORKERS = 50


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    # Requests is loud.  Be quiet requests.
    logging.getLogger("requests").setLevel(logging.WARNING)
    requests.packages.urllib3.disable_warnings()
    # If we're using logging for metrics collection, show it.
    logging.getLogger("ores.metrics_collectors").setLevel(logging.DEBUG)

    stream_url = args['<stream-url>']
    ores_url = args['<ores-url>']
    config_paths = os.path.join(args['--config'], "*.yaml")
    config = yamlconf.load(*(open(p) for p in
                             sorted(glob.glob(config_paths))))
    delay = float(args['--delay'])
    verbose = bool(args['--debug'])
    ss_name = config['ores']['scoring_system']
    if 'metrics_collector' in config['scoring_systems'][ss_name]:
        metrics_collector = MetricsCollector.from_config(
            config, config['scoring_systems'][ss_name]['metrics_collector'])
    else:
        metrics_collector = Null()

    run(stream_url, ores_url, metrics_collector, config, delay,
        verbose)


def run(stream_url, ores_url, metrics_collector, config, delay, verbose):

    # What to do in case of a change
    def precache_a_change(change):
        session = requests.Session()
        if delay:
            time.sleep(delay)
        start = time.time()
        response = session.post(ores_url + "/v3/precache/", json=change, headers={'Content-Type': "Application/JSON"})
        if response.status == 200:
            logger.info("Scored {0} in {1} seconds."
                        .format(json.dumps(change), round(time.time() - start, 3)))
        elif response.status == 204:
            logger.debug("Nothing to do for {0}".format(json.dumps(change)))
        else:
            logger.error("Scoring {0} and got an error in response:\n{1}"
                         .format(json.dumps(change), response.content))

    # Execute changes!
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        for event in SSEClient(stream_url):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                except ValueError:
                    continue

                executor.submit(precache_a_change, change)
