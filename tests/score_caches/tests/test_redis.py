import pytest

from ores.score_caches.redis import Redis as RedisScoreCache
from tests.redis_mock import RedisMock


@pytest.fixture
def cache():
    return RedisScoreCache.from_config({
        'score_caches': {
            'redis': {
                'host': 'localhost',
                'prefix': 'ores-derp',
                'ttl': 100}}}, 'redis')


@pytest.mark.redis
def test_lookup(cache):
    cache.store(0.421, 'testwiki', 'damaging', 124)
    assert cache.lookup('testwiki', 'damaging', 124) == 0.421


@pytest.fixture
def cache_mock():
    return RedisScoreCache(RedisMock(), 0, 'foo')


@pytest.mark.redis
def test_lookup_mock(cache_mock):
    cache_mock.store(0.421, 'testwiki', 'damaging', 124)
    assert cache_mock.lookup('testwiki', 'damaging', 124) == 0.421
