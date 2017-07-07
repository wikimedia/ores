import celery

from ..celery_queue import CeleryQueue
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
