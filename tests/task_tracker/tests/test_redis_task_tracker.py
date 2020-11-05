import pytest

from ores.task_tracker.redis_task_tracker import RedisTaskTracker
from tests.redis_mock import RedisMock


@pytest.fixture
def task_tracker():
    """
    Return a task object.

    Args:
    """
    return RedisTaskTracker.from_config({
        'task_trackers': {
            'redis': {
                'host': 'localhost',
                'prefix': 'ores-derp',
                'ttl': 100}}}, 'redis')


@pytest.mark.redis
def test_lock(task_tracker):
    """
    Test if task lock.

    Args:
        task_tracker: (todo): write your description
    """
    assert task_tracker.lock('fooo', 'value1') is True


@pytest.mark.redis
def test_get_in_progress_task(task_tracker):
    """
    Get information about progress of a task.

    Args:
        task_tracker: (todo): write your description
    """
    task_tracker.lock('fooo_get', 'value2')
    assert task_tracker.get_in_progress_task('fooo_get') == 'value2'


@pytest.mark.redis
def test_release(task_tracker):
    """
    Release the lock.

    Args:
        task_tracker: (todo): write your description
    """
    key = 'fooo_release'
    task_tracker.lock(key, 'value3')
    assert task_tracker.release(key)
    assert task_tracker.get_in_progress_task(key) is False


@pytest.fixture
def mock_task_tracker():
    """
    Return a task - safe.

    Args:
    """
    return RedisTaskTracker(RedisMock(), 0, 'foo')


def test_lock_mock(mock_task_tracker):
    """
    Test if the lock.

    Args:
        mock_task_tracker: (todo): write your description
    """
    assert mock_task_tracker.lock('fooo', 'value1') is True


def test_get_in_progress_task_mock(mock_task_tracker):
    """
    Get a mock - progress.

    Args:
        mock_task_tracker: (todo): write your description
    """
    mock_task_tracker.lock('fooo_get', 'value2')
    assert mock_task_tracker.get_in_progress_task('fooo_get') == 'value2'


def test_release_mock(mock_task_tracker):
    """
    Release a mock lock.

    Args:
        mock_task_tracker: (todo): write your description
    """
    key = 'fooo_release'
    mock_task_tracker.lock(key, 'value3')
    assert mock_task_tracker.release(key)
    assert mock_task_tracker.get_in_progress_task(key) is False
