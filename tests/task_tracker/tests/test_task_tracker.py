import pytest

from ores.task_tracker.task_tracker import TaskTracker


def test_lock():
    task_tracker = TaskTracker()
    with pytest.raises(NotImplementedError):
        task_tracker.lock('fooo', 'value')


def test_get_in_progress_task():
    task_tracker = TaskTracker()
    with pytest.raises(NotImplementedError):
        task_tracker.get_in_progress_task('fooo')


def test_release():
    task_tracker = TaskTracker()
    with pytest.raises(NotImplementedError):
        task_tracker.release('fooo')
