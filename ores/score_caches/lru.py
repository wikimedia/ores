import logging

from .score_cache import ScoreCache

logger = logging.getLogger(__name__)


class LRU(ScoreCache):

    def __init__(self, size=1024):
        """
        Initialize pylru.

        Args:
            self: (todo): write your description
            size: (int): write your description
        """
        try:
            import pylru
        except ImportError:
            raise ImportError("Could not find pylru.  This packages is " +
                              "required when using ores.score_caches.LRU.")

        self.lru = pylru.lrucache(size)

    def lookup(self, context_name, model_name, rev_id, version=None,
               injection_cache=None):
        """
        Look up a lookup.

        Args:
            self: (todo): write your description
            context_name: (str): write your description
            model_name: (str): write your description
            rev_id: (int): write your description
            version: (str): write your description
            injection_cache: (todo): write your description
        """
        # Deterministic hash of cache values
        cache_hash = hash(tuple(sorted((injection_cache or {}).items())))
        key = (context_name, model_name, rev_id, version, cache_hash)
        logger.debug("Looking up score at {0}".format(key))
        return self.lru[key]

    def store(self, score, context_name, model_name, rev_id, version=None,
              injection_cache=None):
        """
        Stores a cache.

        Args:
            self: (todo): write your description
            score: (todo): write your description
            context_name: (str): write your description
            model_name: (str): write your description
            rev_id: (str): write your description
            version: (str): write your description
            injection_cache: (todo): write your description
        """
        # Deterministic hash of cache values
        cache_hash = hash(tuple(sorted((injection_cache or {}).items())))
        key = (context_name, model_name, rev_id, version, cache_hash)
        logger.debug("Storing score at {0}: {1}".format(key, str(score)[:100]))
        self.lru[key] = score

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        """
        Initialize a configuration object from a configuration file.

        Args:
            cls: (todo): write your description
            config: (todo): write your description
            name: (str): write your description
            section_key: (str): write your description
        """
        section = config[section_key][name]

        return cls(**{k: v for k, v in section.items() if k != "class"})
