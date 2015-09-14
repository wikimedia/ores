"""
Starts a celery worker for ORES.  Note that

Usage:
    celery_worker -h | --help
    celery_worker [--config=<path>] [--verbose]

Options:
    -h --help          Prints this documentation
    --config=<path>    The path to a yaml config file
                       [default: config/ores-localdev.yaml]
    --verbose          Turns up logging level
"""
import logging

import docopt
import yamlconf

from ..score_processors import Celery


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    ores_level = logging.DEBUG if args['--verbose'] else logging.INFO
    logging.getLogger('ores').setLevel(ores_level)

    config = yamlconf.load(open(args['--config']))

    name = config['ores']['score_processor']
    score_processor = Celery.from_config(config, name)

    score_processor.application.worker_main(
        argv=["celery_worker", "--loglevel=INFO"]
    )
