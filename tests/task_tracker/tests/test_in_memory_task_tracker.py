from ores.task_tracker.in_memory_task_tracker import InMemoryTaskTracker


def test_in_memory_task_tracker():
    task_tracker = InMemoryTaskTracker()
    assert task_tracker.lock('fooo', 'value') is True
    assert task_tracker.get_in_progress_task('fooo') == 'value'
    assert task_tracker.release('fooo') is True
    assert task_tracker.get_in_progress_task('fooo') is None
