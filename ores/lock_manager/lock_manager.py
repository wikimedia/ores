"""Lock manager interface."""


class LockManager:
    def connect(self):
        """
        Connect to the lock manager.

        returns false if it wasn't able to connect, true otherwise.
        """
        raise NotImplementedError

    def lock(self, key, workers, maxqueue, timeout):
        """
        Acquire a lock in the lock manager.

        returns false if it wasn't able to lock, true otherwise.
        """
        raise NotImplementedError

    def release(self, key):
        """
        Release the lock in the lock manager.

        returns false if it wasn't able to release, true otherwise.
        """
        raise NotImplementedError

    def close(self):
        """
        Close the connection to the lock manager.

        returns false if it wasn't able to close the connection, true otherwise.
        """
        raise NotImplementedError
