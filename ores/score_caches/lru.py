from .score_cache import ScoreCache


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
        return self.lru[(wiki, model, rev_id, version, cache_hash)]

    def store(self, wiki, model, rev_id, score, version=None, cache=None):
        # Deterministic hash of cache values
        cache_hash = hash(tuple(sorted((cache or {}).items())))
        self.lru[(wiki, model, rev_id, version, cache_hash)] = score

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        section = config[section_key][name]

        return cls(**{k: v for k, v in section.items() if k != "class"})
