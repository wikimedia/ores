import json

import pytest

from ores.applications.wsgi import build


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


def test_scores_v1_404_context(client):
    res = client.get('/v1/scores/noowiki/', follow_redirects=True)
    data = json.loads(res.get_data().decode('utf-8'))
    assert res.status_code == 404
    assert data == {'error': {'code': 'not found', 'message': 'No scorers available for noowiki'}}


def test_scores_v1_context_model(client):
    res = client.get('/v1/scores/testwiki/revid', follow_redirects=True)
    data = json.loads(res.get_data().decode('utf-8'))
    del data['statistics']
    assert res.status_code == 200
    assert data == {'behavior': 'Returns the last two digits in a rev_id as a score.',
                    'type': 'RevIDScorer',
                    'version': '0.0.0'}


def test_scores_v1_404_context_model(client):
    res = client.get('/v1/scores/testwiki/norevic', follow_redirects=True)
    data = json.loads(res.get_data().decode('utf-8'))
    assert res.status_code == 404
    assert data == {'error': {'code': 'not found', 'message': "Models ('norevic',) not available for testwiki"}}


def test_scores_v1_context_rev(client):
    res = client.get('/v1/scores/testwiki/revid/123', follow_redirects=True)
    data = json.loads(res.get_data().decode('utf-8'))
    assert res.status_code == 200
    assert data == {'123': {'prediction': False,
                            'probability': {'false': 0.6799999999999999, 'true': 0.32}}}


def test_scores_v2(client):
    res = client.get('/v2/scores', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'scores': {'testwiki': {'revid': {'version': '0.0.0'}}}}


def test_scores_v2_context(client):
    res = client.get('/v2/scores/testwiki/', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'scores': {'testwiki': {'revid': {'version': '0.0.0'}}}}


def test_scores_v2_404_context(client):
    res = client.get('/v2/scores/noowiki/', follow_redirects=True)
    assert res.status_code == 404
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'error': {'code': 'not found', 'message': 'No scorers available for noowiki'}}


def test_scores_v2_context_model(client):
    res = client.get('/v2/scores/testwiki/revid', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'scores': {'testwiki': {'revid': {'version': '0.0.0'}}}}


def test_scores_v2_context_404_model(client):
    res = client.get('/v2/scores/testwiki/revidd', follow_redirects=True)
    assert res.status_code == 404
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'error': {'code': 'not found',
                      'message': "Models ('revidd',) not available for testwiki"}}


def test_scores_v2_context_rev(client):
    res = client.get('/v2/scores/testwiki/revid/123', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'scores': {'testwiki': {'revid': {'scores': {'123': {'prediction': False,
                                                                 'probability': {'false': 0.6799999999999999,
                                                                                 'true': 0.32}}},
                                              'version': '0.0.0'}}}}


def test_scores_v3(client):
    res = client.get('/v3/scores', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'testwiki': {'models': {'revid': {'version': '0.0.0'}}}}


def test_scores_v3_context(client):
    res = client.get('/v3/scores/testwiki/', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'testwiki': {'models': {'revid': {'version': '0.0.0'}}}}


def test_scores_v3_404_context(client):
    res = client.get('/v3/scores/noowiki/', follow_redirects=True)
    assert res.status_code == 404
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'error': {'code': 'not found', 'message': 'No scorers available for noowiki'}}


def test_scores_v3_rev(client):
    res = client.get('/v3/scores/testwiki/123', follow_redirects=True)
    assert res.status_code == 200
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'testwiki': {'models': {'revid': {'version': '0.0.0'}},
                         'scores': {'123': {'revid': {'score': {'prediction': False,
                                                                'probability': {'false': 0.6799999999999999,
                                                                                'true': 0.32}}}}}}}


def test_scores_v3_precache_get(client):
    res = client.get('/v3/precache', follow_redirects=True)
    assert res.status_code == 405


def test_scores_v3_precache_bad_data(client):
    res = client.post('/v3/precache', follow_redirects=True)
    assert res.status_code == 400
    assert json.loads(res.get_data().decode('utf-8')) == \
           {'error': {'code': 'bad request',
                      'message': "Must provide a POST'ed json as an event"}}
