from ..score_request import ScoreRequest


def test_score_request():
    sr = ScoreRequest("foo", [1, 2, 3], ["bar", "baz"], ip='0.0.0.0')

    assert sr.context_name == "foo"
    assert sr.rev_ids == {1, 2, 3}
    assert sr.model_names == {"bar", "baz"}
    assert sr.precache is False
    assert sr.include_features is False
    assert sr.model_info is None
    assert sr.ip == '0.0.0.0'


def test_score_request_serialization():
    sr = ScoreRequest("foo", [1, 2, 3], ["bar", "baz"], ip='0.0.0.0')

    assert sr.toJSON() == {
        'context': 'foo',
        'include_features': False,
        'injection_caches': {},
        'ip': '0.0.0.0',
        'model_info': None,
        'model_names': {'bar', 'baz'},
        'precache': False,
        'rev_ids': {1, 2, 3}}


def test_score_request_deserialization():
    sr = ScoreRequest("foo", [1, 2, 3], ["bar", "baz"], ip='0.0.0.0')
    sr_new = ScoreRequest.fromJSON({
        'context': 'foo',
        'include_features': False,
        'injection_caches': {},
        'ip': '0.0.0.0',
        'model_info': None,
        'model_names': {'bar', 'baz'},
        'precache': False,
        'rev_ids': {1, 2, 3}})

    assert sr.toJSON() == sr_new.toJSON()
