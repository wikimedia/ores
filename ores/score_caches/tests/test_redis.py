import pytest

from ..redis import Redis


@pytest.fixture
def cache():
    return Redis.from_config({
        'score_caches': {
            'redis': {
                'host': 'localhost',
                'prefix': 'ores-derp',
                'ttl': 100}}}, 'redis')


@pytest.mark.redis
def test_lookup(cache):
    cache.store(0.421, 'testwiki', 'damaging', 124)
    assert cache.lookup('testwiki', 'damaging', 124) == 0.421


class RedisMock():
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


@pytest.fixture
def cache_mock():
    return Redis(RedisMock(), 0, 'foo')


@pytest.mark.redis
def test_lookup_mock(cache_mock):
    cache_mock.store(0.421, 'testwiki', 'damaging', 124)
    assert cache_mock.lookup('testwiki', 'damaging', 124) == 0.421
