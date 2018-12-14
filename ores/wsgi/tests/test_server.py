import pytest
import json

from ...applications.wsgi import build


@pytest.fixture
def client():
    yield build().test_client()


def test_home(client):
    res = client.get('/', follow_redirects=True)
    assert res.status_code == 200


def test_404(client):
    res = client.get('/404', follow_redirects=True)
    assert res.status_code == 404


def test_scores(client):
    res = client.get('/scores', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'contexts': ['testwiki']}


def test_scores_v1_context(client):
    res = client.get('/v1/scores/testwiki/', follow_redirects=True)
    data = json.loads(res.get_data().decode('utf-8'))
    del data['models']['revid']['statistics']
    assert res.status_code == 200
    assert data == {'models': {'revid': {
        'version': '0.0.0',
        'type': 'RevIDScorer',
        'behavior': 'Returns the last two digits in a rev_id as a score.'
    }}}


def test_scores_v2_context(client):
    res = client.get('/v2/scores/testwiki/', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'scores': {'testwiki': {'revid': {'version': '0.0.0'}}}}


def test_scores_v3_context(client):
    res = client.get('/v3/scores/testwiki/', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'testwiki': {'models': {'revid': {'version': '0.0.0'}}}}
