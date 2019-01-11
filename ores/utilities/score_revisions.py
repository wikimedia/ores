"""
Scores a set of revisions using an ORES api

Usage:
    score_revisions (-h|--help)
    score_revisions <ores-host> <user-agent> <context> <model>...
                    [--batch-size=<revs>]
                    [--parallel-requests=<reqs>]
                    [--retries=<num>]
                    [--input=<path>]
                    [--input-format=<input-format>]
                    [--output=<path>]
                    [--debug]
                    [--verbose]

Examples:
    echo '{"rev_id": 12345}' | \
        ores score_revisions https://ores.wikimedia.org srwiki damaging

Options:
    -h --help        Prints this documentation
    <ores-host>      The base URL to an ORES instance to use in scoring.
                     TODO: Make optional.
                     [example: https://ores.wikimedia.org]
    <user-agent>     The user agent to provide to the ORES service for tracking
                     purposes.  Good user agents include an email address that
                     admins can contact.
                     [example: "<someone@domain.org> Analyzing article hist"]
    <context>        The name of the wiki to execute model(s) for.
                     [example: srwiki]
    <model>          The name of a model to use in scoring
                     [example: damaging]
    --batch-size=<revs>  The number of scores to batch per request.
                         [default: 50]
    --parallel-requests=<reqs>  The size of the requester pool.  This limits
                                maximum number of concurrent connections.
                                [default: 2]
    --retries=<num>  The maximum number of retries for basic HTTP errors
                     before giving up. [default: 5]
    --input=<path>   A file listing revision IDs.  See --input-format for the
                     available formats.
                     [default: <stdin>]
    --input-format=<format>  Format of the input records.
                     If the format is "jsonlines", then we parse each line as a
                     JSON object with a top-level "rev_id" field.
                     for example: {"rev_id": 12345}
                     If the format is "plain", each line is a raw revision ID: 12345
                     [default: jsonlines]
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
    user_agent = args['<user-agent>']
    context = args['<context>']
    model_names = args['<model>']
    batch_size = int(args['--batch-size'])
    parallel_requests = int(args['--parallel-requests'])
    retries = int(args['--retries'])
    input_format = args['--input-format']
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

    run(ores_host, user_agent, context, model_names, batch_size,
        parallel_requests, retries, input, input_format, output, verbose)


def run(ores_host, user_agent, context, model_names, batch_size,
        parallel_requests, retries, input, input_format, output, verbose):
    session = api.Session(
        ores_host, user_agent=user_agent, batch_size=batch_size,
        parallel_requests=parallel_requests, retries=retries)

    if input_format == "jsonlines":
        rev_docs = [json.loads(l) for l in input]
        rev_ids = [d['rev_id'] for d in rev_docs]
    elif input_format == "plain":
        rev_ids = [int(l.strip()) for l in input.readlines()]
        rev_docs = [{"rev_id": rev_id} for rev_id in rev_ids]
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
