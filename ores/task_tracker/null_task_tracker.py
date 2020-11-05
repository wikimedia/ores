"""
Null implementation of task tracker.
"""

from .task_tracker import TaskTracker


class NullTaskTracker(TaskTracker):
    def lock(self, key, task_id):
        """
        Lock a task.

        Args:
            self: (todo): write your description
            key: (str): write your description
            task_id: (str): write your description
        """
        return True

    def get_in_progress_task(self, key):
        """
        Get the task task task.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        return None

    def release(self, key):
        """
        Release the lock. lock.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        return True
