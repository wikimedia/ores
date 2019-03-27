class RedisMock:
    def __init__(self):
        self.values = {}

    def setex(self, key, ttl, value):
        self.values[key] = value
        return True

    def get(self, key):
        return self.values.get(key)

    def delete(self, key):
        del self.values[key]
        return True
