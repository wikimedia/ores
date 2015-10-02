import time

from nose.tools import eq_
from revscoring.features import Feature
from revscoring.scorer_models import ScorerModel

from ...scoring_contexts import ScoringContext
from ..timeout import Timeout

wait_time = Feature("wait_time", returns=float)


class FakeSM(ScorerModel):

    def __init__(self):
        self.features = [wait_time]
        self.language = None
        self.version = None

    def score(self, feature_values):
        raise NotImplementedError()


class FakeSC(ScoringContext):

    def solve(self, model, cache):
        return cache

    def score(self, model, cache):
        wait_time_value = cache[wait_time]
        time.sleep(wait_time_value)
        return {'score': True}

    def extract_roots(self, model, rev_ids, caches=None):
        return {rev_id: (None, caches[rev_id]) for rev_id in rev_ids}


def test_score():
    fakewiki = FakeSC("fakewiki", {'fake': FakeSM()}, None)
    score_processor = Timeout({'fakewiki': fakewiki}, timeout=0.10)

    scores = score_processor.score("fakewiki", "fake", [1],
                                   caches={1: {wait_time: 0.05}})
    eq_(scores, {1: {'score': True}})


def test_timeout():
    fakewiki = FakeSC("fakewiki", {'fake': FakeSM()}, None)
    score_processor = Timeout({'fakewiki': fakewiki}, timeout=0.05)

    scores = score_processor.score("fakewiki", "fake", [1],
                                   caches={1: {wait_time: 0.10}})
    assert 'error' in scores[1]
    assert 'Timed out after' in scores[1]['error']['message']
