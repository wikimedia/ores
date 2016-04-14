"""
Starts a celery worker for ORES.  Note that

Usage:
    celery_worker -h | --help
    celery_worker [--config=<path>] [--verbose]

Options:
    -h --help          Prints this documentation
    --config=<path>    The path to a yaml config file
                       [default: config]
    --verbose          Turns up logging level
"""
import docopt
import glob
import logging
import os
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

    config_paths = os.path.join(args['--config'], "*.yaml")
    config = yamlconf.load(*(open(p) for p in
                             sorted(glob.glob(config_paths))))

    name = config['ores']['score_processor']
    score_processor = Celery.from_config(config, name)

    score_processor.application.worker_main(
        argv=["celery_worker", "--loglevel=INFO"]
    )
