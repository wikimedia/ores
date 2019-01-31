"""
In memory implementation of task tracker. Used for tests.
"""

from .task_tracker import TaskTracker


class InMemoryTaskTracker(TaskTracker):

    def __init__(self):
        self.tasks = {}

    def lock(self, key, task_id):
        self.tasks[key] = task_id
        return True

    def get_in_progress_task(self, key):
        return self.tasks.get(key)

    def release(self, key):
        del self.tasks[key]
        return True
