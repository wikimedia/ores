"""
Runs a celery worker process that exposes a task API for
ores.scoring_systems.CeleryQueue

Usage:
    celery [--config-dir=<path>]... [--logging-config=<path>]
           [--debug] [--verbose]

Options:
    -h --help                Prints this documentation
    --config-dir=<path>      The path to a directory containing configuration
                             [default: config/]
    --logging-config=<path>  The path to a logging configuration file
    --debug                  Print debug logging information
    --verbose                Print verbose extraction information
"""
import logging

import docopt

from ..scoring_systems import CeleryQueue
from .util import build_config


def main(argv=None):
    args = docopt.docopt(__doc__, argv=argv)
    verbose = args['--verbose']
    debug = args['--debug']

    run(verbose, debug,
        config_dirs=args['--config-dir'],
        logging_config=args['--logging-config'])


def run(verbose, debug, **kwargs):
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
    )
    logging.getLogger('requests').setLevel(logging.INFO)
    if verbose:
        logging.getLogger('revscoring.dependencies.dependent') \
               .setLevel(logging.DEBUG)
    else:
        logging.getLogger('revscoring.dependencies.dependent') \
               .setLevel(logging.INFO)

    logging.getLogger("ores.metrics_collectors.logger").setLevel(logging.DEBUG)
    logging.getLogger("stopit").setLevel(logging.ERROR)

    application = build(**kwargs)
    logging.getLogger('ores').setLevel(logging.DEBUG)
    celery_log_level = "DEBUG" if debug else "INFO"
    application.worker_main(
        argv=["celery_worker", "--loglevel=" + celery_log_level])


def build(*args, **kwargs):
    config = build_config(*args, **kwargs)
    scoring_system = CeleryQueue.from_config(
        config, config['ores']['scoring_system'])
    return scoring_system.application
