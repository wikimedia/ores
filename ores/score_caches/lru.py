import logging

from .score_cache import ScoreCache

logger = logging.getLogger(__name__)


class LRU(ScoreCache):

    def __init__(self, size=1024):
        try:
            import pylru
        except ImportError:
            raise ImportError("Could not find pylru.  This packages is " +
                              "required when using ores.score_caches.LRU.")

        self.lru = pylru.lrucache(size)

    def lookup(self, wiki, model, rev_id, version=None, cache=None):
        # Deterministic hash of cache values
        cache_hash = hash(tuple(sorted((cache or {}).items())))
        key = (wiki, model, rev_id, version, cache_hash)
        logger.debug("Looking up score at {0}".format(key))
        return self.lru[key]

    def store(self, wiki, model, rev_id, score, version=None, cache=None):
        # Deterministic hash of cache values
        cache_hash = hash(tuple(sorted((cache or {}).items())))
        key = (wiki, model, rev_id, version, cache_hash)
        logger.debug("Storing score at {0}".format(key))
        self.lru[key] = score

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        section = config[section_key][name]

        return cls(**{k: v for k, v in section.items() if k != "class"})
