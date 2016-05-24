import logging

from .metrics_collector import MetricsCollector


class Logger(MetricsCollector):
    """
    A metrics collector that uses :mod:`logging` to report usage metrics.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def precache_request(self, context_name, model_names, duration):
        self.logger.debug("precache_request: {0}:{1} in {2} seconds"
                          .format(context_name, model_names, duration))

    def scores_request(self, context_name, model_names, rev_id_count,
                       duration):
        self.logger.debug(
            "scores_request: {0}:{1} for {2} revisions in {3} seconds"
            .format(context_name, model_names, rev_id_count, duration))

    def datasources_extracted(self, context_name, model_names, rev_id_count,
                              duration):
        self.logger.debug(
            "datasources_extracted: {0}:{1} for {2} revisions in {3} secs"
            .format(context_name, model_names, rev_id_count, duration))

    def score_processor_overloaded(self, context_name, model_names, count=1):
        self.logger.debug("score_processor_overloaded: " +
                          "{0}:{1}".format(context_name, model_names))

    def score_processed(self, context_name, model_names, duration):
        self.logger.debug("score_processed: {0}:{1} in {2} seconds"
                          .format(context_name, model_names, duration))

    def score_cache_hit(self, context_name, model_names, count=1):
        for i in range(count):
            self.logger.debug("score_cache_hit: {0}:{1}"
                              .format(context_name, model_names))

    def score_errored(self, context_name, model_names, count=1):
        for i in range(count):
            self.logger.debug("score_errored: {0}:{1}"
                              .format(context_name, model_names))

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
            local_logging:
                class: ores.metrics_collectors.Logging
        """
        return cls()
