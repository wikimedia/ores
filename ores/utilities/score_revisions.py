"""
Scores a set of revisions using an ORES api

Usage:
    score_revisions (-h|--help)
    score_revisions <ores-host> <context> <model>...
                    [--input=<path>]
                    [--output=<path>]
                    [--debug]
                    [--verbose]

Options:
    -h --help        Prints this documentation
    <ores-host>      The host name for an ORES instance to use in scoring
    <context>        The name of the wiki to execute model(s) for
    <model>          The name of a model to use in scoring
    --input=<path>   A file containing json blobs with "rev_id" fields
                     [default: <stdin>]
    --output=<path>  A file to write json blobs with scores to
                     [default: <stdout>]
    --debug          Print debug logging
    --verbose        Print out dots to sterr
"""
import json
import logging
import sys

import docopt

from .. import api

logger = logging.getLogger(__name__)


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO if not args['--debug'] else logging.DEBUG,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    if not args['--debug']:
        logging.getLogger("requests.packages.urllib3").setLevel(logging.WARNING)

    ores_host = args['<ores-host>']
    context = args['<context>']
    model_names = args['<model>']
    if args['--input'] == "<stdin>":
        logger.info("Reading input from <stdin>")
        input = sys.stdin
    else:
        logger.info("Reading input from {0}".format(args['--input']))
        input = open(args['--input'])
    if args['--output'] == "<stdout>":
        logger.info("Writing output to from <stdout>")
        output = sys.stdout
    else:
        logger.info("Writing output to {0}".format(args['--output']))
        output = open(args['--output'], "w")

    verbose = args['--verbose']

    run(ores_host, context, model_names, input, output, verbose)


def run(ores_host, context, model_names, input, output, verbose):
    rev_docs = [json.loads(l) for l in input]
    session = api.Session(ores_host, user_agent="ahalfaker@wikimedia.org")

    rev_ids = [d['rev_id'] for d in rev_docs]
    scores = session.score(context, model_names, rev_ids)

    for rev_doc, score_doc in zip(rev_docs, scores):
        rev_doc['score'] = score_doc
        json.dump(rev_doc, sys.stdout)
        sys.stdout.write("\n")
        if verbose:
            sys.stderr.write(".")
            sys.stderr.flush()


if __name__ == "__main__":
    main()
