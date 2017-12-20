import glob
import os.path
import yamlconf
import logging
import logging.config
import sys

DEFAULT_DIRS = ["config/", "/etc/ores/"]
DEFAULT_LOGGING_CONFIG = "logging_config.yaml"
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


def configure_logging(verbose=False, debug=False, logging_config=None, **kwargs):
    # Load logging config if specified.  If no config file is specified, we
    # make a half-hearted attempt to find a distributed logging_config.yaml
    # in the current working directory.
    if logging_config is None:
        if os.path.exists(DEFAULT_LOGGING_CONFIG):
            logging_config = DEFAULT_LOGGING_CONFIG

    if logging_config is not None:
        with open(logging_config) as f:
            logging_config = yamlconf.load(f)
            logging.config.dictConfig(logging_config)

        # Secret sauce: if running from the console, mirror logs there.
        if sys.stdin.isatty():
            handler = logging.StreamHandler(stream=sys.stdout)
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
