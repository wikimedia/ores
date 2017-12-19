import glob
import os.path
import yamlconf
import logging
import logging.config

DEFAULT_DIRS = ["config/", "/etc/ores/"]


logger = logging.getLogger(__name__)


def build_config(config_dirs=DEFAULT_DIRS):
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


def configure_logging(verbose, debug, logging_config=None):
    # Load logging config if specified
    if logging_config is not None:
        with open(logging_config) as f:
            logging_config = yamlconf.load(f)
            logging.config.dictConfig(logging_config)

    else:
        # Configure fallback logging.
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s %(levelname)s:%(name)s -- %(message)s'
        )
        logging.getLogger('requests').setLevel(logging.INFO)
        logging.getLogger('ores.metrics_collectors.logger').setLevel(logging.DEBUG)
        logging.getLogger('stopit').setLevel(logging.ERROR)

    # Command-line options can override some of the logging config, regardless
    # of whether logging_config.yaml was provided.
    if verbose:
        logging.getLogger('revscoring.dependencies.dependent') \
               .setLevel(logging.DEBUG)
