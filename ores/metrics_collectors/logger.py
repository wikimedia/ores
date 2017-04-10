import logging

from .metrics_collector import MetricsCollector
from .util import format_set


class Logger(MetricsCollector):
    """
    A metrics collector that uses :mod:`logging` to report usage metrics.
    """
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def precache_request(self, request, duration):
        self.logger.debug(
            "precache_request: {0}:{1} in {2} seconds"
            .format(request.context_name, format_set(request.model_names),
                    round(duration, 3)))

    def scores_request(self, request, duration):
        self.logger.debug(
            "scores_request: {0}:{1} for {2} revisions in {3} seconds"
            .format(request.context_name, format_set(request.model_names),
                    len(request.rev_ids), round(duration, 3)))

    def datasources_extracted(self, request, rev_id_count, duration):
        self.logger.debug(
            "datasources_extracted: {0}:{1} for {2} revisions in {3} secs"
            .format(request.context_name, format_set(request.model_names),
                    rev_id_count, round(duration, 3)))

    def score_processor_overloaded(self, request, count=1):
        self.logger.debug(
            "score_processor_overloaded: " +
            "{0}:{1}".format(request.context_name,
                             format_set(request.model_names)))

    def score_processed(self, request, duration):
        self.logger.debug(
            "score_processed: {0}:{1} in {2} seconds"
            .format(request.context_name, format_set(request.model_names),
                    round(duration, 3)))

    def score_timed_out(self, request, duration):
        self.logger.debug(
            "score_timed_out: {0}:{1} in {2} seconds"
            .format(request.context_name, format_set(request.model_names),
                    round(duration, 3)))

    def score_cache_hit(self, request, model_name):
        if request.precache:
            self.logger.debug("precache_cache_hit: {0}:{1}"
                              .format(request.context_name, model_name))
        else:
            self.logger.debug("score_cache_hit: {0}:{1}"
                              .format(request.context_name, model_name))

    def score_cache_miss(self, request, model_name):
        if request.precache:
            self.logger.debug("precache_cache_miss: {0}:{1}"
                              .format(request.context_name, model_name))
        else:
            self.logger.debug("score_cache_miss: {0}:{1}"
                              .format(request.context_name, model_name))

    def score_errored(self, request, model_name):
        self.logger.debug("score_errored: {0}:{1}"
                          .format(request.context_name, model_name))

    def precache_score(self, request, duration):
        self.logger.debug("precache_score: {0}:{1} in {2} seconds"
                          .format(request.context_name,
                                  format_set(request.model_names),
                                  round(duration, 3)))

    def precache_scoring_error(self, request, status, duration):
        self.logger.debug(
            "precache_scoring_error: {0}:{1} status={2} in {3} seconds"
            .format(request.context_name, format_set(request.model_names),
                    status, round(duration, 3)))

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
            local_logging:
                class: ores.metrics_collectors.Logging
        """
        return cls()
