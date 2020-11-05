import flask
import pytest
from ores.applications.wsgi import build
from ores.scoring_systems.scoring_system import ScoringSystem
from ores.wsgi.util import (build_event_set, build_precache_map,
                            build_score_request,
                            build_score_request_from_event)


@pytest.fixture
def app():
    """
    Yields the app.

    Args:
    """
    yield build()


def test_build_score_request(app):
    """
    The test test request.

    Args:
        app: (todo): write your description
    """
    with app.test_request_context('/?models=foo|bar&revids=123|234', environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        scoring_system = ScoringSystem({})
        actual = build_score_request(scoring_system, flask.request).to_json()
        actual['model_names'].sort()
        actual['rev_ids'].sort()

        expected = {
             'context': None,
             'include_features': False,
             'injection_caches': {},
             'ip': '127.0.0.1',
             'model_info': [],
             'model_names': ['bar', 'foo'],
             'precache': False,
             'rev_ids': [123, 234]
        }
        assert actual == expected


def test_build_score_request_(app):
    """
    The test test test.

    Args:
        app: (todo): write your description
    """
    with app.test_request_context('/?models=foo&precache&features', environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        scoring_system = ScoringSystem({})
        actual = build_score_request(scoring_system, flask.request, context_name='testwiki', rev_id=7251).to_json()

        expected = {
            'context': 'testwiki',
            'include_features': True,
            'injection_caches': {},
            'ip': '127.0.0.1',
            'model_info': [],
            'model_names': ['foo'],
            'precache': True,
            'rev_ids': [7251]
        }
        assert actual == expected


def test_build_score_request_injection(app):
    """
    Builds a test test test.

    Args:
        app: (todo): write your description
    """
    with app.test_request_context(
            '/?models=foo&revids=123|234&feature.foo.bar=1',
            environ_base={'REMOTE_ADDR': '127.0.0.1'}):
        scoring_system = ScoringSystem({})
        actual = build_score_request(scoring_system, flask.request, context_name='testwiki', rev_id=None).to_json()

        expected = {
            'context': 'testwiki',
            'include_features': False,
            'injection_caches': {123: {"feature.foo.bar": 1}, 234: {"feature.foo.bar": 1}},
            'ip': '127.0.0.1',
            'model_info': [],
            'model_names': ['foo'],
            'precache': False,
            'rev_ids': [234, 123]
        }
        assert actual == expected


def test_build_precache_map():
    """
    Generate a build map

    Args:
    """
    precache_config = {
        'revid': {'on': ['edit']}, 'goodfaith': {'on': ['edit']}
    }
    config = {
        'ores': {
            'scoring_system': 'test'
        },
        'scoring_systems': {
            'test': {
                'scoring_contexts': ['enwiki']
            }
        },
        'scoring_contexts': {'enwiki': {'precache': precache_config}}
    }
    precache_map = build_precache_map(config)
    assert precache_map == {'enwiki': {'edit': {'revid', 'goodfaith'}}}


def test_build_event_set():
    """
    Build a test events.

    Args:
    """
    event = {
        'rev_content_model': 'wikitext',
        'page_is_redirect': False,
        'rev_content_format': 'text/x-wiki',
        'rev_sha1': '3vv5u9bvaeycx0t0w6n7jjwdpyzc951',
        'rev_parent_id': 931601209,
        'page_id': 57951304,
        'page_namespace': 0,
        '$schema': '/mediawiki/revision/create/1.0.0',
        'rev_timestamp': '2019-12-19T22:55:34Z',
        'meta': {
            'request_id': 'Xfv-5gpAIDEAAEU91qkAAABY',
            'partition': 0,
            'domain': 'en.wikipedia.org',
            'dt': '2019-12-19T22:55:34Z',
            'stream': 'mediawiki.revision-create',
            'uri': 'https://en.wikipedia.org/wiki/Sidhu_Moose_Wala',
            'topic': 'eqiad.mediawiki.revision-create',
            'offset': 1542189973,
            'id': '5a048c0d-5401-45f1-8559-ff08d0f241b0'
        },
        'performer': {
            'user_text': '184.68.29.42',
            'user_groups': ['*'],
            'user_is_bot': False
        },
        'rev_minor_edit': False,
        'page_title': 'Sidhu_Moose_Wala',
        'rev_len': 13771,
        'rev_id': 931601462,
        'rev_content_changed': True,
        'chronology_id': '2f8df00917ebf7ffd684492af76d6724',
        'database': 'enwiki'}
    assert build_event_set(event) == {"edit", "main_edit", "nonbot_edit"}


def test_event():
    """
    Generate a test event.

    Args:
    """
    event = {
        "database": "enwiki",
        "meta": {
            "stream": "mediawiki.revision-create"
        },
        "page_id": 193804,
        "page_is_redirect": False,
        "page_namespace": 0,
        "page_title": "TestArticleForORES",
        "performer": {
            "user_edit_count": 1281,
            "user_groups": ["bureaucrat", "sysop", "*", "user"],
            "user_id": 6591,
            "user_is_bot": False,
            "user_registration_dt": "2015-09-02T18:00:37Z",
            "user_text": "Pchelolo"
        },
        "rev_content_changed": False,
        "rev_content_format": "text/x-wiki",
        "rev_content_model": "wikitext",
        "rev_id": 387768,
        "rev_len": 77,
        "rev_minor_edit": False,
        "rev_parent_id": 387767,
        "rev_sha1": "1820ao45y9o91b8m5tojay0yrsn15kh",
        "rev_timestamp": "2018-12-13T16:53:16Z"}

    precache_map = {'enwiki': {'main_edit': {'revid', 'goodfaith'}, 'bot_edit': {'damaging'}}}
    expected = {
        'context': 'enwiki',
        'include_features': False,
        'injection_caches': {},
        'ip': None,
        'model_info': None,
        'model_names': ['goodfaith', 'revid'],
        'precache': True,
        'rev_ids': [387768]
    }

    actual = build_score_request_from_event(precache_map, event).to_json()
    actual['model_names'].sort()
    assert actual == expected
