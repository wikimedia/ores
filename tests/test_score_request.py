from ores.score_request import ScoreRequest


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
    actual = sr.to_json()
    actual['model_names'].sort()
    actual['rev_ids'].sort()

    assert actual == {
        'context': 'foo',
        'include_features': False,
        'injection_caches': {},
        'ip': '0.0.0.0',
        'model_info': None,
        'model_names': ['bar', 'baz'],
        'precache': False,
        'rev_ids': [1, 2, 3]}


def test_score_request_deserialization():
    sr = ScoreRequest("foo", [1, 2, 3], ["bar", "baz"], ip='0.0.0.0')
    sr_new = ScoreRequest.from_json({
        'context': 'foo',
        'include_features': False,
        'injection_caches': {},
        'ip': '0.0.0.0',
        'model_info': None,
        'model_names': {'bar', 'baz'},
        'precache': False,
        'rev_ids': {1, 2, 3}})

    assert sr.to_json() == sr_new.to_json()
