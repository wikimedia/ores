import socket
from contextlib import contextmanager

from nose.tools import eq_, raises

from ...score_request import ScoreRequest
from ..statsd import Statsd


def test_statsd():
    class StatsClient:

        def __init__(self):
            self.messages = []

        def incr(self, name, count=1):
            self.messages.append(("INCR", name, count))

        def timing(self, name, duration):
            self.messages.append(("TIMING", name, duration))

        @contextmanager
        def pipeline(self):
            yield self

    fake_client = StatsClient()

    collector = Statsd(fake_client)
    collector.precache_request(ScoreRequest("foo", [1], {"bar", "derp"}), 100)
    collector.scores_request(ScoreRequest("foo", list(range(50)), {"bar"}), 150)
    collector.datasources_extracted(ScoreRequest("foo", [1], {"bar"}), 10, 25)
    collector.score_processed(ScoreRequest("foo", [1], {"bar"}), 1.1)
    collector.score_timed_out(ScoreRequest("foo", [1], {"bar"}), 15.1)
    collector.score_cache_miss(ScoreRequest("foo", [1], {"derp"}), "derp")
    collector.score_cache_hit(ScoreRequest("foo", [1], {"bar"}), "bar")
    collector.score_errored(ScoreRequest("foo", [1], {"bar"}), "bar")

    eq_(set(fake_client.messages) -
        {('TIMING', 'precache_request.foo.derp', 100000),
         ('TIMING', 'precache_request.foo.bar', 100000),
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
         ('TIMING', 'score_processed.foo.bar', 1100.0),
         ('TIMING', 'score_processed.foo', 1100.0),
         ('TIMING', 'score_processed', 1100.0),
         ('TIMING', 'score_timed_out.foo.bar', 15100.0),
         ('TIMING', 'score_timed_out.foo', 15100.0),
         ('TIMING', 'score_timed_out', 15100.0),
         ('INCR', 'score_cache_miss.foo.derp', 1),
         ('INCR', 'score_cache_miss.foo', 1),
         ('INCR', 'score_cache_miss', 1),
         ('INCR', 'score_cache_hit.foo.bar', 1),
         ('INCR', 'score_cache_hit.foo', 1),
         ('INCR', 'score_cache_hit', 1),
         ('INCR', 'score_errored.foo.bar', 1),
         ('INCR', 'score_errored.foo', 1),
         ('INCR', 'score_errored', 1)},
        set())


@raises(socket.gaierror)
def test_from_config():
    # Should throw a socket connection error and no others
    config = {
        'metrics_collectors': {
            'wmflabs_statsd': {
                'class': 'ores.metrics_collectors.Statsd',
                'host': 'totally.doesnt.exists.OMG',
                'prefix': 'ores.{hostname}',
                'maxudpsize': 512
            }
        }
    }
    Statsd.from_config(config, 'wmflabs_statsd')
