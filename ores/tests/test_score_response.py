from nose.tools import eq_

from ..score_request import ScoreRequest
from ..score_response import ScoreResponse


class FakeContext:

    def __init__(self, name):
        self.name = name


def test_score_request():
    sr = ScoreResponse(
        FakeContext("foowiki"),
        ScoreRequest("foo", [1, 2, 3], ["bar", "baz"]))

    sr.add_score(1, "bar", {"prediction": False})
    sr.add_score(1, "baz", {"prediction": True})
    sr.add_features(1, "baz", {"feature.rev_id": 1})
    sr.add_error(2, "bar", Exception("WTF"))
    sr.add_error(2, "baz", Exception("WTF"))
    sr.add_score(3, "bar", {"prediction": True})
    sr.add_score(3, "baz", {"prediction": False})
    sr.add_features(3, "baz", {"feature.rev_id": 3})

    eq_(sr.scores[3]['baz']['prediction'], False)
