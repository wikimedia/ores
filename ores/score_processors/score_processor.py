
import os
import signal

from .util import timeout


class ScoreResult():
    def get(self, *args, **kwargs):
        raise NotImplementedError()


class ScoreProcessor:

    def process(self, scorer_model, extractor, cache):
        raise NotImplementedError()


class SimpleScoreResult():

    def __init__(self, score):
        self.score = score

    def get(self):
        return self.score

def process_score(scorer_model, extractor, cache):
    # TODO: record time spend extracting features
    features = list(extractor.solve(scorer_mode.features, cache=cache))

    # TODO: resord time spent generating a score
    score = scorer_model.score(feature)

    return score
