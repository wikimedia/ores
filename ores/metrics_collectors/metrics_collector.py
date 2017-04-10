import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects metrics about usage of ORES.
    """
    def precache_request(self, request, duration):
        raise NotImplementedError()

    def scores_request(self, request, duration):
        raise NotImplementedError()

    def datasources_extracted(self, request, rev_id_count, duration):
        raise NotImplementedError()

    def score_processor_overloaded(self, request):
        raise NotImplementedError()

    def score_processed(self, request, duration):
        raise NotImplementedError()

    def score_cache_hit(self, request, model_name):
        raise NotImplementedError()

    def score_cache_miss(self, request, model_name):
        raise NotImplementedError()

    def score_errored(self, request, model_name):
        raise NotImplementedError()

    def score_timed_out(self, request, duration):
        raise NotImplementedError()

    def precache_scores(self, request, duration):
        raise NotImplementedError()

    def precache_scoring_error(self, request, status, duration):
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
