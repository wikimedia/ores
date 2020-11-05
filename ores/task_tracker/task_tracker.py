"""
Interface for task trackers.
"""


class TaskTracker:
    def lock(self, key, task_id):
        """
        Lock a task.

        Args:
            self: (todo): write your description
            key: (str): write your description
            task_id: (str): write your description
        """
        raise NotImplementedError

    def get_in_progress_task(self, key):
        """
        Get the task task task.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        raise NotImplementedError

    def release(self, key):
        """
        Release the lock.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        raise NotImplementedError
