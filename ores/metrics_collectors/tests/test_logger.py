from collections import namedtuple

from nose.tools import eq_

from ..logger import Logger


def test_logger():
    messages = []
    FakeLogger = namedtuple("Logger", ["debug"])
    logging_logger = FakeLogger(lambda m: messages.append(m))

    collector = Logger(logging_logger)
    collector.precache_request("foo", "bar", "0.0.1", 100)
    collector.scores_request("foo", "bar", "0.0.1", 50, 150)
    collector.datasources_extracted("foo", "bar", "0.0.1", 10, 25)
    collector.score_processed("foo", "bar", "0.0.1", 1.1)
    collector.score_cache_hit("foo", "bar", "0.0.1", 2)
    collector.score_errored("foo", "bar", "0.0.1")

    eq_(messages,
        ['precache_request: foo.bar.0.0.1 in 100 seconds',
         'scores_request: foo.bar.0.0.1 for 50 revisions in 150 seconds',
         'datasources_extracted: foo.bar.0.0.1 for 10 revisions in 25 seconds',
         'score_processed: foo.bar.0.0.1 in 1.1 seconds',
         'score_cache_hit: foo.bar.0.0.1',
         'score_cache_hit: foo.bar.0.0.1',
         'score_errored: foo.bar.0.0.1'])


def test_from_config():
    # Should throw a socket connection error and no others
    config = {
        'metrics_collectors': {
            'logger': {
                'class': 'ores.metrics_collectors.Logger'
            }
        }
    }
    Logger.from_config(config, 'logger')
