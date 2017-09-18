from ..score_request import ScoreRequest


def test_score_request():
    sr = ScoreRequest("foo", [1, 2, 3], ["bar", "baz"])

    assert sr.context_name == "foo"
    assert sr.rev_ids == {1, 2, 3}
    assert sr.model_names == {"bar", "baz"}
    assert sr.precache is False
    assert sr.include_features is False
    assert sr.model_info is None
