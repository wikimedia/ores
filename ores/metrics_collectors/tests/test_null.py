from ..null import Null


def test_null():
    # Make sure we throw no errors.

    collector = Null()
    collector.precache_request("foo", "bar", "0.0.1", 100)
    collector.scores_request("foo", "bar", "0.0.1", 50, 150)
    collector.datasources_extracted("foo", "bar", "0.0.1", 10, 25)
    collector.score_processed("foo", "bar", "0.0.1", 1.1)
    collector.score_cache_hit("foo", "bar", "0.0.1", 2)
    collector.score_errored("foo", "bar", "0.0.1")


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
