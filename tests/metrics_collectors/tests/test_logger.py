from collections import namedtuple

from ores.metrics_collectors.logger import Logger
from ores.score_request import ScoreRequest


def test_logger():
    messages = []
    FakeLogger = namedtuple("Logger", ["debug"])
    logging_logger = FakeLogger(lambda m: messages.append(m))

    collector = Logger(logging_logger)
    collector.precache_request(ScoreRequest("foo", [1], {"bar", "derp"}), 100)
    collector.scores_request(ScoreRequest("foo", list(range(50)), {"bar"}), 150)
    collector.datasources_extracted(ScoreRequest("foo", [1], {"bar"}), 10, 25)
    collector.score_processed(ScoreRequest("foo", [1], {"bar"}), 1.1)
    collector.score_timed_out(ScoreRequest("foo", [1], {"bar"}), 15.1)
    collector.score_cache_miss(ScoreRequest("foo", [1], {"derp"}), "derp")
    collector.score_cache_hit(ScoreRequest("foo", [1], {"bar"}), "bar")
    collector.score_errored(ScoreRequest("foo", [1], {"bar"}), "bar")
    collector.lock_acquired('pulpcounter', 3)
    collector.response_made(404, ScoreRequest("foo", [1], {"bar"}))

    assert set(messages) == \
        {"precache_request: foo:{'bar', 'derp'} in 100 seconds",
         "scores_request: foo:{'bar'} for 50 revisions in 150 seconds",
         "datasources_extracted: foo:{'bar'} for 10 revisions in 25 secs",
         "score_processed: foo:{'bar'} in 1.1 seconds",
         "score_timed_out: foo:{'bar'} in 15.1 seconds",
         "score_cache_miss: foo:derp",
         "score_cache_hit: foo:bar",
         "score_errored: foo:bar",
         "locking_response_time: pulpcounter in 3 seconds",
         "Response code 404 in foo context"}


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
