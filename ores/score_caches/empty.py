from .score_cache import ScoreCache


class Empty(ScoreCache):

    def lookup(self, *args, **kwargs):
        raise KeyError()

    def store(self, *args, **kwargs):
        return None
