from .metrics_collector import MetricsCollector


class Null(MetricsCollector):
    """
    A non-metrics collector that does nothing.
    """
    def precache_request(self, context, model, version, duration):
        pass

    def scores_request(self, context, model, version, rev_id_count, duration):
        pass

    def datasources_extracted(self, context, model, version, rev_id_count,
                              duration):
        pass

    def score_processed(self, context, model, version, incr=1):
        pass

    def score_cache_hit(self, context, model, version, incr=1):
        pass

    def score_errored(self, context, model, version, incr=1):
        pass

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
        local_logging:
        class: ores.metrics_collectors.Logging
        """
        return cls()
