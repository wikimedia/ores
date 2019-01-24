"""
Null implementation of task tracker.
"""

from .task_tracker import TaskTracker


class NullTaskTracker(TaskTracker):
    def lock(self, key, task_id):
        return True

    def get_in_progress_task(self, key):
        return None

    def release(self, key):
        return True
