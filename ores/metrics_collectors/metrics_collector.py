import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects metrics about usage of ORES.
    """
    def precache_request(self, context, model, duration):
        raise NotImplementedError()

    def scores_request(self, context, model, rev_id_count, duration):
        raise NotImplementedError()

    def datasources_extracted(self, context, model, rev_id_count, duration):
        raise NotImplementedError()

    def score_processed(self, context, model, duration):
        raise NotImplementedError()

    def score_cache_hit(self, context, model, inc=1):
        raise NotImplementedError()

    def score_errored(self, context, model, inc=1):
        raise NotImplementedError()

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        try:
            import yamlconf
        except ImportError:
            raise ImportError("Could not find yamlconf.  This packages is " +
                              "required when using yaml config files.")
        logger.info("Loading MetricsCollector '{0}' from config.".format(name))
        section = config[section_key][name]
        if 'module' in section:
            return yamlconf.import_module(section['module'])
        elif 'class' in section:
            Class = yamlconf.import_module(section['class'])
            return Class.from_config(config, name)