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
