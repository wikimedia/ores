"""
Starts a celery worker for ORES.  Note that

Usage:
    celery_worker -h | --help
    celery_worker [--config=<path>]

Options:
    -h --help          Prints this documentation
    --config=<path>    The path to a yaml config file
                       [default: config/ores-localdev.yaml]
"""
import logging

import docopt
import yamlconf

from ..score_processors import Celery


def main(argv=None):
    logging.basicConfig(level=logging.DEBUG)
    args = docopt.docopt(__doc__, argv=argv)

    config = yamlconf.load(open(args['--config']))

    name = config['ores']['score_processor']
    score_processor = Celery.from_config(config, name)

    score_processor.application.worker_main(
        argv=["celery_worker", "--loglevel=INFO"]
    )
