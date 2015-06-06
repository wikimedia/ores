import pylru

from .score_cache import ScoreCache


class LRU(ScoreCache):

    def __init__(self, size=1024):
        self.lru = pylru.lrucache(size)

    def lookup(self, wiki, model, rev_id, version=None):
        return self.lru[(wiki, model, rev_id, version)]

    def store(self, wiki, model, rev_id, score, version=None):
        self.lru[(wiki, model, rev_id, version)] = score

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        section = config[section_key][name]

        return cls(**{k:v for k,v in section.items() if k != "class"})
