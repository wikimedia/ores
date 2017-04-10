import time

from nose.tools import eq_, nottest
from revscoring import Extractor, ScorerModel
from revscoring.features import Feature

from ...score_request import ScoreRequest
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

    response = scoring_system.score(
        ScoreRequest("fakewiki", [1], ["fake"],
                     injection_caches={1: {wait_time: 0.05}},
                     model_info=['version']))
    eq_(response.errors, {})
    eq_(response.scores, {1: {'fake': True}})
    eq_(response.model_info, {'fake': {'version': 'fake version'}})

    response = scoring_system.score(
        ScoreRequest("fakewiki", [1, 2], ["fake", "other_fake"],
                     injection_caches={1: {wait_time: 0.05},
                                       2: {wait_time: 0.01}},
                     model_info=['version']))
    eq_(response.errors, {})
    eq_(response.scores,
        {1: {'fake': True, 'other_fake': True},
         2: {'fake': True, 'other_fake': True}})
    eq_(response.model_info, {'fake': {'version': 'fake version'},
                              'other_fake': {'version': 'fake version'}})
