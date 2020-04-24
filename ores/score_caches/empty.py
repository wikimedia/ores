from .score_cache import ScoreCache


class Empty(ScoreCache):

    def lookup(self, *args, **kwargs):
        raise KeyError()

    def store(self, *args, **kwargs):
        return None

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        return cls()
