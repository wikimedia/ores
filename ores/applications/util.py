import glob
import os.path
import yamlconf
import logging.config

DEFAULT_DIRS = ["config/", "/etc/ores/"]


def build_config(config_dirs=DEFAULT_DIRS,
                 logging_config="logging_config.yaml"):
    config_paths = []
    for directory in config_dirs:
        config_paths.extend(glob.glob(os.path.join(directory, "*.yaml")))
    config_paths.sort()
    config = yamlconf.load(*(open(p) for p in config_paths))

    if logging_config is not None:
        with open(logging_config) as f:
            logging_config = yamlconf.load(f)
            logging.config.dictConfig(logging_config)

    if 'data_paths' in config['ores'] and \
       'nltk' in config['ores']['data_paths']:
        import nltk
        nltk.data.path.append(config['ores']['data_paths']['nltk'])

    return config
