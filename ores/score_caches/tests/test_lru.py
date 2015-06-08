from nose.tools import eq_

from ..lru import LRU
from ..score_cache import ScoreCache


def test_lru():
    lru = LRU(2)

    cache_context = lru.context("foo", "bar")

    cache_context.store(1, "foo")
    cache_context.store(2, "bar")
    cache_context.store(3, "baz")  # 1 gets bumped

    eq_(cache_context.lookup(2), "bar")  # Moves 2 to the front
    cache_context.store(4, "fez")  # 3 gets bumped

    eq_(cache_context.lookup(2), "bar")  # Moves 2 to the front
    eq_(cache_context.lookup(4), "fez")  # Moves 4 to the front


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
    eq_(context.lookup(1), "foo")
