import glob
import logging
import logging.config
import os.path
import sys

import yamlconf

DEFAULT_DIRS = ["config/", "/etc/ores/"]
DEFAULT_FORMAT = "%(asctime)s %(levelname)s:%(name)s -- %(message)s"


logger = logging.getLogger(__name__)


def build_config(config_dirs=DEFAULT_DIRS, **kwargs):
    # Loads files in alphabetical order based on the bare filename
    config_file_paths = []
    for directory in config_dirs:
        dir_glob = os.path.join(directory, "*.yaml")
        config_file_paths.extend((os.path.basename(path), path)
                                 for path in glob.glob(dir_glob))
    config_file_paths.sort()
    logger.info("Loading configs from {0}".format(config_file_paths))
    config = yamlconf.load(*(open(p) for fn, p in config_file_paths))

    # Add nltk data path if specified.
    if 'data_paths' in config['ores'] and \
       'nltk' in config['ores']['data_paths']:
        import nltk
        nltk.data.path.append(config['ores']['data_paths']['nltk'])

    return config


def configure_logging(verbose=False, debug=False, config=None, **kwargs):
    if config is None:
        logging_config = None
    else:
        logging_config = config.get('logging')

    if logging_config is not None:
        logging.config.dictConfig(logging_config)

        # Secret sauce: if running from the console, mirror logs there.
        if sys.stdin.isatty():
            handler = logging.StreamHandler(stream=sys.stderr)
            formatter = logging.Formatter(fmt=DEFAULT_FORMAT)
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)

    else:
        # Configure fallback logging.
        logging.basicConfig(level=logging.INFO, format=DEFAULT_FORMAT)
        logging.getLogger('requests').setLevel(logging.INFO)
        logging.getLogger('stopit').setLevel(logging.ERROR)

    # Command-line options can override some of the logging config, regardless
    # of whether logging_config.yaml was provided.
    # TODO: Document and reconcile debug vs verbose.
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('ores.metrics_collectors.logger') \
               .setLevel(logging.DEBUG)

    if verbose:
        logging.getLogger('revscoring.dependencies.dependent') \
               .setLevel(logging.DEBUG)
