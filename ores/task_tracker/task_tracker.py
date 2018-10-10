"""
Interface for task trackers.
"""


class TaskTracker:
    def lock(self, key, task_id):
        raise NotImplementedError

    def get_in_progress_task(self, key):
        raise NotImplementedError

    def release(self, key):
        raise NotImplementedError
