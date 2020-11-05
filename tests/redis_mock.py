class RedisMock:
    def __init__(self):
        """
        Initialize the values.

        Args:
            self: (todo): write your description
        """
        self.values = {}

    def setex(self, key, ttl, value):
        """
        Sets the value for a given key.

        Args:
            self: (todo): write your description
            key: (str): write your description
            ttl: (int): write your description
            value: (todo): write your description
        """
        self.values[key] = value
        return True

    def get(self, key):
        """
        Return the value from the given key.

        Args:
            self: (todo): write your description
            key: (todo): write your description
        """
        return self.values.get(key)

    def delete(self, key):
        """
        Removes a key from the cache.

        Args:
            self: (todo): write your description
            key: (str): write your description
        """
        del self.values[key]
        return True
