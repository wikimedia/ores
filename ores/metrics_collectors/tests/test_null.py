from ..null import Null


def test_null():
    # Make sure we throw no errors.

    collector = Null()
    collector.precache_request("foo", {"bar", "derp"}, 100)
    collector.scores_request("foo", {"bar"}, 50, 150)
    collector.datasources_extracted("foo", {"bar"}, 10, 25)
    collector.score_processed("foo", {"bar"}, 1.1)
    collector.score_timed_out("foo", {"bar"}, 15.1)
    collector.score_cache_miss("foo", {"bar", "derp"}, 1)
    collector.score_cache_hit("foo", {"bar"}, 2)
    collector.score_errored("foo", {"bar"})


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
