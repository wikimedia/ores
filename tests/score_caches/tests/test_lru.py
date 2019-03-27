from pytest import raises

from ores.score_caches.lru import LRU
from ores.score_caches.score_cache import ScoreCache


def test_lru():
    lru = LRU(2)

    cache_context = lru.context("foo", "bar")

    cache_context.store(1, "foo")
    cache_context.store(2, "bar")
    cache_context.store(3, "baz")  # 1 gets bumped

    assert cache_context.lookup(2) == "bar"  # Moves 2 to the front
    cache_context.store(4, "fez")  # 3 gets bumped

    assert cache_context.lookup(2) == "bar"  # Moves 2 to the front
    assert cache_context.lookup(4) == "fez"  # Moves 4 to the front


def test_lru_cache():
    lru = LRU(2)

    cache_context = lru.context("foo", "bar")

    cache_context.store(1, "foo")
    cache_context.store(1, "cachedfoo", injection_cache={"cachedvalue": 1})

    assert cache_context.lookup(1, injection_cache={"cachedvalue": 1}) == \
        "cachedfoo"
    assert cache_context.lookup(1) == "foo"

    with raises(KeyError):
        cache_context.lookup(1, injection_cache={"cachedvalue": 2})


def test_from_config():
    config = {
        'score_caches': {
            'mycache': {
                'class': 'ores.score_caches.LRU',
                'size': 128
            }
        }
    }

    cache = ScoreCache.from_config(config, "mycache")
    context = cache.context("foo", "bar")
    context.store(1, "foo")
    assert context.lookup(1) == "foo"
