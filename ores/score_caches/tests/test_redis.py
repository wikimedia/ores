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


def test_lookup(cache):
    cache.store(0.421, 'teswiki', 'damaging', 124)
    assert cache.lookup('teswiki', 'damaging', 124) == 0.421
