import pytest

from ..redis_task_tracker import RedisTaskTracker


@pytest.fixture
def task_tracker():
    return RedisTaskTracker.from_config({
        'task_trackers': {
            'redis': {
                'host': 'localhost',
                'prefix': 'ores-derp',
                'ttl': 100}}}, 'redis')


@pytest.mark.redis
def test_lock(task_tracker):
    assert task_tracker.lock('fooo', 'value1') is True


@pytest.mark.redis
def test_get_in_progress_task(task_tracker):
    task_tracker.lock('fooo_get', 'value2')
    assert task_tracker.get_in_progress_task('fooo_get') == 'value2'


@pytest.mark.redis
def test_release(task_tracker):
    task_tracker.lock('fooo_release', 'value3')
    assert task_tracker.release('fooo_release')
    assert task_tracker.get_in_progress_task('fooo_release') is False
