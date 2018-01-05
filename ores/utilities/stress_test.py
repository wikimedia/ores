"""
Runs a stress test against an ORES api by sending it requests at a configurable
rate.

:Usage:
    stress_test -h | --help
    stress_test <context> <ores-url>...
                [--model=<name>]
                [--batch-size=<n>]
                [--delay=<secs>]
                [--input=<path>]
                [--debug]
                [--verbose]

:Options:
    -h --help          Prints this documentation
    <ores-url>         URL of base ORES webserver.  If multiple URLS are
                       provided, they will be cycled through round-robin.
    <context>          The context in which to request scores
    -m --model=<name>  What models to request?  If none are provided, all
                       available models will be scored.
    --batch-size=<n>   The number of revision IDs should included in a single
                       request [default: 1]
    --delay=<secs>     The delay between requests (rpm = 60/delay) [default: 1]
    --input=<path>     The path to a file containing JSON blobs with a 'rev_id'
                       field. [default: <stdin>]
    --debug            Print debugging information
    --verbose          Print dots and stuff to stderr
"""
import logging
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle, islice

import docopt
import requests
from revscoring.utilities.util import read_observations

logger = logging.getLogger(__name__)
REQUEST_THREADS = 1000


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    # Requests is loud.  Be quiet requests.
    requests.packages.urllib3.disable_warnings()

    ores_urls = args['<ores-url>']
    context = args['<context>']
    if args['--input'] == "<stdin>":
        rev_ids = [ob['rev_id'] for ob in read_observations(sys.stdin)]
    else:
        rev_ids = [
            ob['rev_id'] for ob in read_observations(open(args['--input']))]
    if args['--model'] is None:
        models = []
    else:
        models = args['--model']

    batch_size = int(args['--batch-size'])
    delay = float(args['--delay'])
    verbose = args['--verbose']

    run(ores_urls, context, models, rev_ids, batch_size, delay, verbose)


def run(ores_urls, context, models, rev_ids, batch_size, delay, verbose):
    url_cycle = cycle(ores_urls)
    rev_ids_cycle = cycle(rev_ids)
    stats = defaultdict(int)
    stats["requests"] = defaultdict(int)
    stats["responses"] = defaultdict(int)
    stats["model_scored"] = defaultdict(int)
    stats["model_errored"] = defaultdict(lambda: defaultdict(int))

    start = time.time()
    with ThreadPoolExecutor(max_workers=REQUEST_THREADS) as executor:
        try:
            while time.sleep(delay) is None:
                ores_url = next(url_cycle)
                rev_id_batch = list(islice(rev_ids_cycle, batch_size))
                logger.debug("Submitting {0} rev_ids to {1}...".format(
                    len(rev_ids), ores_url))
                executor.submit(request_and_stat, ores_url, context,
                                models, rev_id_batch, stats, verbose)
        except KeyboardInterrupt:
            print("Caught keyboard interrupt...")
            print("Stats:")
            duration = time.time() - start
            print("  Duration: {0}s".format(round(duration, 3)))
            print("  Requests: {0} ({1} per minute)".format(
                stats['total_requests'],
                round(stats['total_requests'] / (duration / 60), 3)))
            print("  Responses:", stats['total_responses'])
            for status_code, count in stats['responses'].items():
                print("   - {0}: {1}".format(status_code, count))
            print("  Score requests:")
            print("   - errored:", stats['score_requests_errored'])
            print("   - returned:", stats['score_requests_returned'])
            print("  Model scores:")
            print("   - successes:")
            for name, count in stats['model_scored'].items():
                print("     - {0}: {1}".format(name, count))
            print("   - errored:")
            for name, type_doc in stats['model_errored'].items():
                print("     - {0}:".format(name))
                for type, count in type_doc.items():
                    print("       - {0}: {1}".format(type, count))


def request_and_stat(ores_url, context, models, rev_ids, stats, verbose):
    path = "/v3/scores/{0}/".format(context)
    logger.debug("Requesting {0} rev_ids...".format(len(rev_ids)))
    params = {'revids': "|".join(str(r) for r in rev_ids),
              'features': ""}
    if models:
        params = {'models': "|".join(models)}

    stats['total_requests'] += 1
    try:
        response = requests.get(
            ores_url + path, params=params)
    except Exception:
        stats['responses']['connection error'] += 1
        return

    logger.debug("{0} response for {1} rev_ids...".format(
        response.status_code, len(rev_ids)))
    stats['total_responses'] += 1
    stats['responses'][response.status_code] += 1

    if response.status_code >= 200 and response.status_code < 300:
        sys.stderr.write(".")
        sys.stderr.flush()
    elif response.status_code == 503:
        sys.stderr.write("!")
        sys.stderr.flush()
    else:
        sys.stderr.write("?")
        sys.stderr.flush()

    try:
        doc = response.json()
    except ValueError:
        stats['non_json_responses'] += 1
        return

    if 'error' in doc:
        stats['score_requests_errored'] += 1
    elif context in doc:
        stats['score_requests_returned'] += 1

        for rev_id_str in doc[context]['scores']:
            stats['revisions_scored'] += 1
            for name, score_doc in doc[context]['scores'][rev_id_str].items():
                if 'error' in score_doc:
                    type_name = score_doc['error']['type']
                    stats['model_errored'][name][type_name] += 1
                else:
                    stats['model_scored'][name] += 1

    return
