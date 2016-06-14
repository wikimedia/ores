"""
Runs a celery worker.

Usage:
    celery [--config-dir=<path>]... [--logging-config=<path>]

Options:
    -h --help                Prints this documentation
    --config-dir=<path>      The path to a directory containing configuration
                             [default: config/]
    --logging-config=<path>  The path to a logging configuration file
"""

import logging

import docopt

from ..score_processors import Celery
from .util import build_config


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    run(config_dirs=args['--config-dir'],
        logging_config=args['--logging-config'])


def run(*args, **kwargs):
    application = build(*args, **kwargs)
    logging.getLogger('ores').setLevel(logging.DEBUG)
    application.worker_main(argv=["celery_worker", "--loglevel=INFO"])


def build(*args, **kwargs):
    config = build_config(*args, **kwargs)
    score_processor = Celery.from_config(
        config, config['ores']['score_processor'])
    return score_processor.application
