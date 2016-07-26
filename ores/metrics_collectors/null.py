from .metrics_collector import MetricsCollector


class Null(MetricsCollector):
    """
    A non-metrics collector that does nothing.
    """
    def precache_request(self, context, model_names, duration):
        pass

    def scores_request(self, context, model_names, rev_id_count, duration):
        pass

    def datasources_extracted(self, context, model_names, rev_id_count,
                              duration):
        pass

    def score_processor_overloaded(self, context, model_names):
        pass

    def score_processed(self, context, model_names, duration):
        pass

    def score_timed_out(self, context, model_names, duration):
        pass

    def score_cache_hit(self, context, model_name):
        pass

    def score_cache_miss(self, context, model_name):
        pass

    def score_errored(self, context, model_names):
        pass

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
        local_logging:
        class: ores.metrics_collectors.Logging
        """
        return cls()
