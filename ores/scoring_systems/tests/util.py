from nose.tools import eq_, nottest
import time

from revscoring.features import Feature
from revscoring import ScorerModel
from revscoring import Extractor
from ...scoring_context import ScoringContext

wait_time = Feature("wait_time", returns=float)


def process_wait(wait_time):
    time.sleep(wait_time)
    return wait_time
wait = Feature("wait", process=process_wait, returns=float,
               depends_on=[wait_time])


class FakeSM(ScorerModel):

    def __init__(self):
        self.features = [wait]
        self.version = "fake version"

    def score(self, feature_values):
        return True

    def format_info(self, format=None):
        return {'version': self.version}


class FakeExtractor(Extractor):

    def extract(self, rev_ids, features, *args, **kwargs):
        return [(None, [0 for feature in features]) for rev_id in rev_ids]


fakewiki = ScoringContext(
    "fakewiki", {'fake': FakeSM(), 'other_fake': FakeSM()}, FakeExtractor())


@nottest
def test_scoring_system(scoring_system):

    score_doc = scoring_system.score(
            "fakewiki", ["fake"], [1], injection_caches={1: {wait_time: 0.01}})
    eq_(score_doc['scores'], {1: {'fake': {'score': True}}})
    eq_(score_doc['models'], {'fake': {'version': 'fake version'}})

    score_doc = scoring_system.score(
            "fakewiki", ["fake", "other_fake"], [1, 2],
            injection_caches={1: {wait_time: 0.01}, 2: {wait_time: 0.01}})
    eq_(score_doc['scores'],
        {1: {'fake': {'score': True}, 'other_fake': {'score': True}},
         2: {'fake': {'score': True}, 'other_fake': {'score': True}}})
    eq_(score_doc['models'], {'fake': {'version': 'fake version'},
                              'other_fake': {'version': 'fake version'}})
