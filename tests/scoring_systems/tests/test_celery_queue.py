import celery
from revscoring.extractors import OfflineExtractor

from ores.score_request import ScoreRequest
from ores.scoring.models import RevIdScorer
from ores.scoring_context import ScoringContext
from ores.scoring_systems.celery_queue import CeleryQueue
from ores.task_tracker import InMemoryTaskTracker

from .util import fakewiki


def test_score():
    application = celery.Celery(__name__)
    CeleryQueue(
        {'fakewiki': fakewiki}, application=application, timeout=15)

    # Can't run the following tests because it starts a new thread and that
    # will break our signal timeout strategy.
    # celerytest.start_celery_worker(application, concurrency=1)
    # test_scoring_system(scoring_system)


def test_celery_queue():
    application = celery.Celery(__name__)
    CeleryQueue(
        {'fakewiki': fakewiki}, application=application, timeout=0.10)

    # Can't run the following tests because it starts a new thread and that
    # will break our signal timeout strategy.
    # celerytest.start_celery_worker(application, concurrency=1)
    # response = scoring_system.score(
    #     ScoreRequest("fakewiki", [1], ["fake"],
    #                  injection_caches={1: {wait_time: 0.05}}))
    # assert 1 in response.errors, str(response.errors)
    # assert isinstance(response.errors[1]['fake'], errors.TimeoutError), \
    #        type(response.errors[1]['fake'])


def test_task():
    revid = RevIdScorer(version='0.0.1')
    fakewiki = ScoringContext(
        'fakewiki', {'revid': revid}, OfflineExtractor())
    application = celery.Celery(__name__)
    scoring_system = CeleryQueue(
        {'fakewiki': fakewiki}, application=application, timeout=0.10)
    request = {
        'context': 'fakewiki',
        'rev_ids': [1234],
        'model_names': ['revid'],
        'precache': False,
        'include_features': False,
        'injection_caches': {},
        'ip': None,
        'model_info': None
    }

    actual = scoring_system._process_score_map(request, ['revid'], 1234, {'datasource.revision.id': 1234})

    expected = {'revid': {'score': {'prediction': False,
                                    'probability': {False: 0.5700000000000001, True: 0.43}}}}
    assert actual == expected


def test_locking():
    application = celery.Celery(__name__)
    revid = RevIdScorer(version='0.0.1')
    fakewiki = ScoringContext(
        'fakewiki', {'revid': revid}, OfflineExtractor())
    scoring_system = CeleryQueue(
        {'fakewiki': fakewiki}, application=application, timeout=0., task_tracker=InMemoryTaskTracker())
    request = {
        'context': 'fakewiki',
        'rev_ids': [1234],
        'model_names': ['revid'],
        'precache': False,
        'include_features': False,
        'injection_caches': {},
        'ip': None,
        'model_info': None
    }

    scoring_system._lock_process(['revid'], 123, ScoreRequest.from_json(request), None, 'Task ID')

    assert len(list(scoring_system.task_tracker.tasks.keys())) == 1
    assert list(scoring_system.task_tracker.tasks.values()) == ['Task ID']
    key = list(scoring_system.task_tracker.tasks.keys())[0]

    # We should not assert the exact key as it's internal but we should assert it has the important bits
    assert 'fakewiki' in key
    assert 'revid' in key
    assert '0.0.1' in key
    assert '123' in key
