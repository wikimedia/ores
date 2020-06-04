from ores.metrics_collectors.prometheus import Prometheus
from ores.score_request import ScoreRequest


def test_prometheus(monkeypatch):
    class PrometheusClient:

        def __init__(self):
            self.messages = []

        def incr(self, name, count=1):
            self.messages.append(("INC", name, count))

        def timing(self, name, duration):
            self.messages.append(("SUMMARY", name, duration))

    fake_client = PrometheusClient()

    def mock_send_timing(*request, duration=None):
        for message in Prometheus.generate_messages(request):
            fake_client.timing(message, duration * 1000)

    def mock_send_inc(*request, count=1):
        for message in Prometheus.generate_messages(request):
            fake_client.incr(message, count)

    collector = Prometheus()
    monkeypatch.setattr(collector, 'send_timing_event', mock_send_timing)
    monkeypatch.setattr(collector, 'send_increment_event', mock_send_inc)

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

    print(fake_client.messages)

    assert set(fake_client.messages) == \
        {('SUMMARY', 'precache_request_foo_derp', 100000),
         ('SUMMARY', 'precache_request_foo_bar', 100000),
         ('SUMMARY', 'precache_request_foo', 100000),
         ('SUMMARY', 'precache_request', 100000),
         ('SUMMARY', 'scores_request_foo_bar', 150000),
         ('SUMMARY', 'scores_request_foo', 150000),
         ('SUMMARY', 'scores_request', 150000),
         ('INC', 'revision_scored_foo_bar', 50),
         ('INC', 'revision_scored_foo', 50),
         ('INC', 'revision_scored', 50),
         ('SUMMARY', 'datasources_extracted_foo_bar', 25000),
         ('SUMMARY', 'datasources_extracted_foo', 25000),
         ('SUMMARY', 'datasources_extracted', 25000),
         ('SUMMARY', 'score_processed_foo_bar', 1100.0),
         ('SUMMARY', 'score_processed_foo', 1100.0),
         ('SUMMARY', 'score_processed', 1100.0),
         ('SUMMARY', 'score_timed_out_foo_bar', 15100.0),
         ('SUMMARY', 'score_timed_out_foo', 15100.0),
         ('SUMMARY', 'score_timed_out', 15100.0),
         ('INC', 'score_cache_miss_foo_derp', 1),
         ('INC', 'score_cache_miss_foo', 1),
         ('INC', 'score_cache_miss', 1),
         ('INC', 'score_cache_hit_foo_bar', 1),
         ('INC', 'score_cache_hit_foo', 1),
         ('INC', 'score_cache_hit', 1),
         ('INC', 'score_errored_foo_bar', 1),
         ('INC', 'score_errored_foo', 1),
         ('SUMMARY', 'locking_response_time_pulpcounter', 3000),
         ('SUMMARY', 'locking_response_time', 3000),
         ('INC', 'response_404', 1),
         ('INC', 'response', 1),
         ('INC', 'response_404_foo', 1),
         ('INC', 'score_errored', 1)}
