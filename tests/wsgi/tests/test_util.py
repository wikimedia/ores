import flask
import pytest

from ores.applications.wsgi import build
from ores.scoring_systems.scoring_system import ScoringSystem
from ores.wsgi.util import (build_precache_map, build_score_request,
                            build_score_request_from_event)


@pytest.fixture
def app():
    yield build()


def test_build_score_request(app):
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


def test_event():
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
