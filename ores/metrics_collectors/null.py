from .metrics_collector import MetricsCollector


class Null(MetricsCollector):
    """
    A non-metrics collector that does nothing.
    """
    def precache_request(self, request, duration):
        """
        Precache the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (float): write your description
        """
        pass

    def scores_request(self, request, duration):
        """
        Takes a request for the given number of the given duration.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (str): write your description
        """
        pass

    def datasources_extracted(self, request, rev_id_count, duration):
        """
        Extracted a point.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            rev_id_count: (str): write your description
            duration: (int): write your description
        """
        pass

    def score_processor_overloaded(self, request):
        """
        Overr_processor.

        Args:
            self: (todo): write your description
            request: (todo): write your description
        """
        pass

    def score_processed(self, request, duration):
        """
        Score the given duration.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        pass

    def score_cache_hit(self, request, model_name):
        """
        Score the request_name to request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        pass

    def score_cache_miss(self, request, model_name):
        """
        Called when a request to the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        pass

    def score_errored(self, request, model_name):
        """
        Score the score of a model.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        pass

    def score_timed_out(self, request, duration):
        """
        : parameter out of the given duration.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        pass

    def precache_scores(self, request, duration):
        """
        Precache a list of the given duration.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (float): write your description
        """
        pass

    def precache_scoring_error(self, request, status, duration):
        """
        Called when a request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            status: (str): write your description
            duration: (float): write your description
        """
        pass

    def lock_acquired(self, lock_type, duration):
        """
        Takes a lock.

        Args:
            self: (todo): write your description
            lock_type: (str): write your description
            duration: (float): write your description
        """
        pass

    def response_made(self, response_code, request):
        """
        Called when a request.

        Args:
            self: (todo): write your description
            response_code: (str): write your description
            request: (todo): write your description
        """
        pass

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
        local_logging:
        class: ores.metrics_collectors.Logging
        """
        return cls()
