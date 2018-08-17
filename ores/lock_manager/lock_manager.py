"""Lock manager interface."""


class LockManager:
    def connect(self):
        raise NotImplementedError

    def acq4me(self, key, workers, maxqueue, timeout):
        raise NotImplementedError

    def release(self, key):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
