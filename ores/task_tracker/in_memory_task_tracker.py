"""
In memory implementation of task tracker. Used for tests.
"""

from .task_tracker import TaskTracker


class InMemoryTaskTracker(TaskTracker):

    def __init__(self):
        """
        Initialize the task.

        Args:
            self: (todo): write your description
        """
        self.tasks = {}

    def lock(self, key, task_id):
        """
        Lock a task.

        Args:
            self: (todo): write your description
            key: (str): write your description
            task_id: (str): write your description
        """
        self.tasks[key] = task_id
        return True

    def get_in_progress_task(self, key):
        """
        Get the progress of a task.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        return self.tasks.get(key)

    def release(self, key):
        """
        Releases the lock.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        del self.tasks[key]
        return True
