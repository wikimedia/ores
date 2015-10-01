from ..null import Null


def test_null():
    # Make sure we throw no errors.

    collector = Null()

    collector.precache_request("foo", "bar", 100)

    collector.scores_request("foo", "bar", 50, 150)

    collector.score_processed("foo", "bar", 1)

    collector.score_cache_hit("foo", "bar", 2)

    collector.score_errored("foo", "bar")
