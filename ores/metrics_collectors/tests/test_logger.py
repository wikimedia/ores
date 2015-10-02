from nose.tools import eq_
from collections import namedtuple

from ..logger import Logger


def test_logger():
    messages = []
    FakeLogger = namedtuple("Logger", ["debug"])
    logging_logger = FakeLogger(lambda m: messages.append(m))

    collector = Logger(logging_logger)
    collector.precache_request("foo", "bar", 100)
    collector.scores_request("foo", "bar", 50, 150)
    collector.datasources_extracted("foo", "bar", 10, 25)
    collector.score_processed("foo", "bar", 1.1)
    collector.score_cache_hit("foo", "bar", 2)
    collector.score_errored("foo", "bar")

    eq_(messages,
        ['precache_request: foo.bar in 100 seconds',
         'scores_request: foo.bar.50 in 150 seconds',
         'datasources_extracted: foo.bar.10 in 25 seconds',
         'score_processed: foo.bar in 1.1 seconds',
         'score_cache_hit: foo.bar',
         'score_cache_hit: foo.bar',
         'score_errored: foo.bar'])
