from ...score_request import ScoreRequest
from ..null import Null


def test_null():
    # Make sure we throw no errors.

    collector = Null()
    collector.precache_request(ScoreRequest("foo", [1], {"bar", "derp"}), 100)
    collector.scores_request(ScoreRequest("foo", list(range(50)), {"bar"}), 150)
    collector.datasources_extracted(ScoreRequest("foo", [1], {"bar"}), 10, 25)
    collector.score_processed(ScoreRequest("foo", [1], {"bar"}), 1.1)
    collector.score_timed_out(ScoreRequest("foo", [1], {"bar"}), 15.1)
    collector.score_cache_miss(ScoreRequest("foo", [1], {"derp"}), "derp")
    collector.score_cache_hit(ScoreRequest("foo", [1], {"bar"}), "bar")
    collector.score_errored(ScoreRequest("foo", [1], {"bar"}), "bar")


def test_from_config():
    # Should throw a socket connection error and no others
    config = {
        'metrics_collectors': {
            'null': {
                'class': 'ores.metrics_collectors.Null'
            }
        }
    }
    Null.from_config(config, 'null')
