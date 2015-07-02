"""
Starts a celery worker for ORES.  Note that

Usage:
    celery_worker -h | --help
    celery_worker <score_processor> [--config=<path>]

Options:
    -h --help          Prints this documentation
    <score_processor>  The name of a score processor to configure
    --config=<path>    The path to a yaml config file
                       [default: config/ores-localdev.yaml]
"""
import logging

import docopt

import yamlconf

from ..score_processors import celery


def main(argv=None):
    logging.basicConfig(level=logging.DEBUG)
    args = docopt.docopt(__doc__, argv=argv)

    config = yamlconf.load(open(args['--config']))

    section_name = args['<score_processor>']

    application = celery.configure(config, section_name)

    application.worker_main(argv=["celery_worker", "--loglevel=INFO"])
