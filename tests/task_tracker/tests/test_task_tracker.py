import pytest

from ores.task_tracker.task_tracker import TaskTracker


def test_lock():
    """
    Test if a task.

    Args:
    """
    task_tracker = TaskTracker()
    with pytest.raises(NotImplementedError):
        task_tracker.lock('fooo', 'value')


def test_get_in_progress_task():
    """
    Get information about progress of the task.

    Args:
    """
    task_tracker = TaskTracker()
    with pytest.raises(NotImplementedError):
        task_tracker.get_in_progress_task('fooo')


def test_release():
    """
    Release task that task.

    Args:
    """
    task_tracker = TaskTracker()
    with pytest.raises(NotImplementedError):
        task_tracker.release('fooo')
