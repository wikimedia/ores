from nose.tools import eq_
from contextlib import contextmanager

from ..statsd import Statsd


def test_statsd():
    class StatsClient:

        def __init__(self):
            self.messages = []

        def incr(self, name, incr=1):
            self.messages.append(("INCR", name, incr))

        def timing(self, name, duration):
            self.messages.append(("TIMING", name, duration))

        @contextmanager
        def pipeline(self):
            yield self

    fake_client = StatsClient()
    collector = Statsd(fake_client)
    collector.precache_request("foo", "bar", 100)
    collector.scores_request("foo", "bar", 50, 150)
    collector.datasources_extracted("foo", "bar", 10, 25)
    collector.score_processed("foo", "bar", 1.1)
    collector.score_cache_hit("foo", "bar", 2)
    collector.score_errored("foo", "bar")

    eq_(fake_client.messages,
        [('TIMING', 'precache_request.foo.bar', 100000),
         ('TIMING', 'precache_request.foo', 100000),
         ('TIMING', 'precache_request', 100000),
         ('TIMING', 'scores_request.foo.bar.50', 150000),
         ('TIMING', 'scores_request.foo.bar', 150000),
         ('TIMING', 'scores_request.foo', 150000),
         ('TIMING', 'scores_request', 150000),
         ('INCR', 'revision_scored.foo.bar', 50),
         ('INCR', 'revision_scored.foo', 50),
         ('INCR', 'revision_scored', 50),
         ('TIMING', 'datasources_extracted.foo.bar.10', 25000),
         ('TIMING', 'datasources_extracted.foo.bar', 25000),
         ('TIMING', 'datasources_extracted.foo', 25000),
         ('TIMING', 'datasources_extracted', 25000),
         ('TIMING', 'score_processed.foo.bar', 1100),
         ('TIMING', 'score_processed.foo', 1100),
         ('TIMING', 'score_processed', 1100),
         ('INCR', 'score_cache_hit.foo.bar', 2),
         ('INCR', 'score_cache_hit.foo', 2),
         ('INCR', 'score_cache_hit', 2),
         ('INCR', 'score_errored.foo.bar', 1),
         ('INCR', 'score_errored.foo', 1),
         ('INCR', 'score_errored', 1)])
