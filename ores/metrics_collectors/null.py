from .metrics_collector import MetricsCollector


class Null(MetricsCollector):
    """
    A non-metrics collector that does nothing.
    """
    def precache_request(self, request, duration):
        pass

    def scores_request(self, request, duration):
        pass

    def datasources_extracted(self, request, rev_id_count, duration):
        pass

    def score_processor_overloaded(self, request):
        pass

    def score_processed(self, request, duration):
        pass

    def score_cache_hit(self, request, model_name):
        pass

    def score_cache_miss(self, request, model_name):
        pass

    def score_errored(self, request, model_name):
        pass

    def score_timed_out(self, request, duration):
        pass

    def precache_scores(self, request, duration):
        pass

    def precache_scoring_error(self, request, status, duration):
        pass

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
        local_logging:
        class: ores.metrics_collectors.Logging
        """
        return cls()
