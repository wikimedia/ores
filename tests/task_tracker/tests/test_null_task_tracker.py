from ores.task_tracker.null_task_tracker import NullTaskTracker


def test_null_task_tracker():
    task_tracker = NullTaskTracker()
    assert task_tracker.lock('fooo', 'value') is True
    assert task_tracker.get_in_progress_task('fooo') is None
    assert task_tracker.release('fooo') is True
