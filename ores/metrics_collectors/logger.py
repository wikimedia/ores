import logging
from .metrics_collector import MetricsCollector


class Logger(MetricsCollector):
    """
    A metrics collector that uses :mod:`logging` to report usage metrics.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def precache_request(self, context, model, duration):
        self.logger.debug("precache_request: {0}.{1} in {2} seconds"
                          .format(context, model, duration))

    def scores_request(self, context, model, rev_id_count, duration):
        self.logger.debug("scores_request: {0}.{1}.{2} in {3} seconds"
                          .format(context, model, rev_id_count, duration))

    def datasources_extracted(self, context, model, rev_id_count, duration):
        self.logger.debug("datasources_extracted: {0}.{1}.{2} in {3} seconds"
                          .format(context, model, rev_id_count, duration))

    def score_processed(self, context, model, duration):
        self.logger.debug("score_processed: {0}.{1} in {2} seconds"
                          .format(context, model, duration))

    def score_cache_hit(self, context, model, incr=1):
        for i in range(incr):
            self.logger.debug("score_cache_hit: {0}.{1}"
                              .format(context, model))

    def score_errored(self, context, model, incr=1):
        for i in range(incr):
            self.logger.debug("score_errored: {0}.{1}"
                              .format(context, model))

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collector"):
        """
        metrics_collectors:
            local_logging:
                class: ores.metrics_collectors.Logging
        """
        return cls()
