import time

from pytest import mark
from revscoring import Extractor, Model
from revscoring.dependencies import solve
from revscoring.features import Feature
from revscoring.scoring import ModelInfo

from ores.score_request import ScoreRequest
from ores.scoring_context import ScoringContext

wait_time = Feature("wait_time", returns=float)


def process_wait(wait_time):
    """
    Process a request and wait for the given timeout.

    Args:
        wait_time: (int): write your description
    """
    time.sleep(wait_time)
    return wait_time


wait = Feature("wait", process=process_wait, returns=float,
               depends_on=[wait_time])


class FakeSM(Model):

    def __init__(self):
        """
        Initialize the info.

        Args:
            self: (todo): write your description
        """
        self.features = [wait]
        self.version = "fake version"
        self.info = ModelInfo()
        self.info['version'] = self.version

    def score(self, feature_values):
        """
        Return the score of the given feature.

        Args:
            self: (todo): write your description
            feature_values: (bool): write your description
        """
        return True


class FakeExtractor(Extractor):

    def extract(self, rev_ids, features, *args, caches={}, **kwargs):
        """
        Extract features from the features.

        Args:
            self: (todo): write your description
            rev_ids: (int): write your description
            features: (todo): write your description
            caches: (dict): write your description
        """
        return [(None, list(solve(features, cache=caches.get(rev_id, {}))))
                for rev_id in rev_ids]


fakewiki = ScoringContext(
    "fakewiki", {'fake': FakeSM(), 'other_fake': FakeSM()}, FakeExtractor())


@mark.skip('Not test')
def test_scoring_system(scoring_system):
    """
    Perform a system system.

    Args:
        scoring_system: (todo): write your description
    """

    response = scoring_system.score(
        ScoreRequest("fakewiki", [1], ["fake"],
                     injection_caches={1: {wait_time: 0.05}},
                     model_info=['version']))
    # Print for debugging.
    print(response.errors)
    assert response.errors == {}
    assert response.scores == {1: {'fake': True}}
    assert response.model_info == {'fake': {'version': 'fake version'}}

    response = scoring_system.score(
        ScoreRequest("fakewiki", [1, 2], ["fake", "other_fake"],
                     injection_caches={1: {wait_time: 0.05},
                                       2: {wait_time: 0.01}},
                     model_info=['version']))
    assert response.errors == {}
    assert response.scores == \
        {1: {'fake': True, 'other_fake': True},
         2: {'fake': True, 'other_fake': True}}
    assert response.model_info == \
        {'fake': {'version': 'fake version'},
         'other_fake': {'version': 'fake version'}}
