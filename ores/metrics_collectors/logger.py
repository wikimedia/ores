import logging

from .metrics_collector import MetricsCollector
from .util import format_set


class Logger(MetricsCollector):
    """
    A metrics collector that uses :mod:`logging` to report usage metrics.
    """
    def __init__(self, logger=None):
        """
        Initialize the logger.

        Args:
            self: (todo): write your description
            logger: (todo): write your description
        """
        self.logger = logger or logging.getLogger(__name__)

    def precache_request(self, request, duration):
        """
        Add the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (float): write your description
        """
        self.logger.debug(
            "precache_request: {0}:{1} in {2} seconds"
            .format(request.context_name, format_set(request.model_names),
                    round(duration, 3)))

    def scores_request(self, request, duration):
        """
        Displays scores for a request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (str): write your description
        """
        self.logger.debug(
            "scores_request: {0}:{1} for {2} revisions in {3} seconds"
            .format(request.context_name, format_set(request.model_names),
                    len(request.rev_ids), round(duration, 3)))

    def datasources_extracted(self, request, rev_id_count, duration):
        """
        Extracted the list of a list of sources.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            rev_id_count: (str): write your description
            duration: (int): write your description
        """
        self.logger.debug(
            "datasources_extracted: {0}:{1} for {2} revisions in {3} secs"
            .format(request.context_name, format_set(request.model_names),
                    rev_id_count, round(duration, 3)))

    def score_processor_overloaded(self, request, count=1):
        """
        Displays the score of the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            count: (int): write your description
        """
        self.logger.debug(
            "score_processor_overloaded: " +
            "{0}:{1}".format(request.context_name,
                             format_set(request.model_names)))

    def score_processed(self, request, duration):
        """
        Displays the score for the given request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        self.logger.debug(
            "score_processed: {0}:{1} in {2} seconds"
            .format(request.context_name, format_set(request.model_names),
                    round(duration, 3)))

    def score_timed_out(self, request, duration):
        """
        Displays the score of the given request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        self.logger.debug(
            "score_timed_out: {0}:{1} in {2} seconds"
            .format(request.context_name, format_set(request.model_names),
                    round(duration, 3)))

    def score_cache_hit(self, request, model_name):
        """
        Displays the cache todo to the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        if request.precache:
            self.logger.debug("precache_cache_hit: {0}:{1}"
                              .format(request.context_name, model_name))
        else:
            self.logger.debug("score_cache_hit: {0}:{1}"
                              .format(request.context_name, model_name))

    def score_cache_miss(self, request, model_name):
        """
        Called when the cache.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        if request.precache:
            self.logger.debug("precache_cache_miss: {0}:{1}"
                              .format(request.context_name, model_name))
        else:
            self.logger.debug("score_cache_miss: {0}:{1}"
                              .format(request.context_name, model_name))

    def score_errored(self, request, model_name):
        """
        Displays the current request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        self.logger.debug("score_errored: {0}:{1}"
                          .format(request.context_name, model_name))

    def precache_score(self, request, duration):
        """
        Displays the score for the given request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        self.logger.debug("precache_score: {0}:{1} in {2} seconds"
                          .format(request.context_name,
                                  format_set(request.model_names),
                                  round(duration, 3)))

    def precache_scoring_error(self, request, status, duration):
        """
        Called when a precache status.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            status: (str): write your description
            duration: (float): write your description
        """
        self.logger.debug(
            "precache_scoring_error: {0}:{1} status={2} in {3} seconds"
            .format(request.context_name, format_set(request.model_names),
                    status, round(duration, 3)))

    def lock_acquired(self, lock_type, duration):
        """
        Lock the lock.

        Args:
            self: (todo): write your description
            lock_type: (str): write your description
            duration: (float): write your description
        """
        self.logger.debug(
            "locking_response_time: {0} in {1} seconds"
            .format(lock_type, round(duration, 3)))

    def response_made(self, response_code, request):
        """
        Handles the request.

        Args:
            self: (todo): write your description
            response_code: (str): write your description
            request: (todo): write your description
        """
        self.logger.debug(
            "Response code {0} in {1} context"
            .format(response_code, request.context_name))

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
            local_logging:
                class: ores.metrics_collectors.Logging
        """
        return cls()
