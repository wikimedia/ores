"""
Null implementation of task tracker.
"""


class NullTaskTracker:
    def lock(self, key, task_id):
        return True

    def get_in_progress_task(self, key):
        return None

    def release(self, key):
        return True
