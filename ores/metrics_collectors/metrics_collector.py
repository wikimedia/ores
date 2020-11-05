import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collects metrics about usage of ORES.
    """
    def precache_request(self, request, duration):
        """
        Precache the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (float): write your description
        """
        raise NotImplementedError()

    def scores_request(self, request, duration):
        """
        Takes a request to the given duration.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (str): write your description
        """
        raise NotImplementedError()

    def datasources_extracted(self, request, rev_id_count, duration):
        """
        Extracted the list of sources.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            rev_id_count: (str): write your description
            duration: (int): write your description
        """
        raise NotImplementedError()

    def score_processor_overloaded(self, request):
        """
        The score score.

        Args:
            self: (todo): write your description
            request: (todo): write your description
        """
        raise NotImplementedError()

    def score_processed(self, request, duration):
        """
        Score the given request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        raise NotImplementedError()

    def score_cache_hit(self, request, model_name):
        """
        Calls cache_cache_hit on the request.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        raise NotImplementedError()

    def score_cache_miss(self, request, model_name):
        """
        Called when a cache score.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        raise NotImplementedError()

    def score_errored(self, request, model_name):
        """
        Shortcut for : meth meth.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            model_name: (str): write your description
        """
        raise NotImplementedError()

    def score_timed_out(self, request, duration):
        """
        Score a score score.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (todo): write your description
        """
        raise NotImplementedError()

    def precache_scores(self, request, duration):
        """
        Precache scores for a given duration.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            duration: (float): write your description
        """
        raise NotImplementedError()

    def precache_scoring_error(self, request, status, duration):
        """
        Called when a request is received.

        Args:
            self: (todo): write your description
            request: (todo): write your description
            status: (str): write your description
            duration: (float): write your description
        """
        raise NotImplementedError()

    def lock_acquired(self, lock_type, duration):
        """
        Lock the lock for a given lock.

        Args:
            self: (todo): write your description
            lock_type: (str): write your description
            duration: (float): write your description
        """
        raise NotImplementedError()

    def response_made(self, response_code, request):
        """
        Handles the response code.

        Args:
            self: (todo): write your description
            response_code: (str): write your description
            request: (todo): write your description
        """
        raise NotImplementedError()

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        Create a class from a configuration file.

        Args:
            cls: (todo): write your description
            config: (todo): write your description
            name: (str): write your description
            section_key: (str): write your description
        """
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
