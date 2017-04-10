from nose.tools import eq_

from ..score_request import ScoreRequest


def test_score_request():
    sr = ScoreRequest("foo", [1, 2, 3], ["bar", "baz"])

    eq_(sr.context_name, "foo")
    eq_(sr.rev_ids, {1, 2, 3})
    eq_(sr.model_names, {"bar", "baz"})
    eq_(sr.precache, False)
    eq_(sr.include_features, False)
    eq_(sr.model_info, None)
