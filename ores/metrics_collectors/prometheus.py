import logging
import prometheus_client
from typing import List

from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class Prometheus(MetricsCollector):
    """
    A metrics collector that uses :mod:`prometheus_client` to report usage metrics.
    """

    def precache_request(self, request, duration: int):
        self.send_timing_event('precache_request', request.context_name,
                               request.model_names, duration=duration)

    def scores_request(self, request, duration: int):
        self.send_timing_event('scores_request', request.context_name,
                               request.model_names, duration=duration)
        self.send_increment_event('revision_scored', request.context_name,
                                  request.model_names,
                                  count=len(request.rev_ids))

    def datasources_extracted(self, request, rev_id_count: int, duration: int):
        self.send_timing_event('datasources_extracted', request.context_name,
                               request.model_names, duration=duration)

    def score_processed(self, request, duration: int):
        self.send_timing_event('score_processed', request.context_name,
                               request.model_names, duration=duration)

    def score_processor_overloaded(self, request):
        self.send_increment_event('score_processor_overloaded',
                                  request.context_name, request.model_names)

    def score_cache_hit(self, request, model_name: str) -> None:
        if request.precache:
            self.send_increment_event(
                'precache_cache_hit', request.context_name, model_name)
        else:
            self.send_increment_event(
                'score_cache_hit', request.context_name, model_name)

    def score_cache_miss(self, request, model_name: str) -> None:
        if request.precache:
            self.send_increment_event(
                    'precache_cache_miss', request.context_name, model_name)
        else:
            self.send_increment_event(
                    'score_cache_miss', request.context_name, model_name)

    def score_errored(self, request, model_name: str) -> None:
        self.send_increment_event('score_errored', request.context_name,
                                  model_name)

    def score_timed_out(self, request, duration: int) -> None:
        self.send_timing_event('score_timed_out', request.context_name,
                               request.model_names, duration=duration)

    def precache_score(self, request, duration: int):
        self.send_timing_event('precache_score', request.context_name,
                               request.model_names, duration=duration)

    def precache_scoring_error(self, request, status, duration: int):
        self.send_timing_event('precache_scoring_error', request.context_name,
                               request.model_names, status, duration=duration)

    def lock_acquired(self, lock_type: str, duration: int):
        self.send_timing_event('locking_response_time', lock_type,
                               duration=duration)

    def response_made(self, response_code, request):
        self.send_increment_event('response', response_code,
                                  request.context_name)

    def send_timing_event(self, *message_parts, duration=None):
        for message in self.generate_messages(message_parts):
            c = prometheus_client.Summary(message, '')
            c.observe(duration * 1000)

    def send_increment_event(self, *message_parts, count=1):
        for message in self.generate_messages(message_parts):
            c = prometheus_client.Counter(message, '')
            c.inc(count)

    @classmethod
    def generate_messages(cls, parts: List[str]):
        """
        Performs a deterministic first walk of the tree implied by a list of
        message parts.

        generate_messages(["foo", "bar", ["herp", "derp"], "baz"]) yields:
        * "foo"
        * "foo_bar"
        * "foo_bar_herp"
        * "foo_bar_herp_baz"
        * "foo_bar_derp"
        * "foo_bar_derp_baz"
        """
        for message_parts in cls.generate_message_parts(parts):
            yield "_".join(message_parts)

    @classmethod
    def generate_message_parts(cls, parts: List[str], i=0, message=[]):
        if len(message) > 0:
            yield message

        if i < len(parts):
            for bpart in cls.branch_message_part(parts[i]):
                yield from cls.generate_message_parts(
                    parts, i=i + 1, message=message + [bpart])

    @classmethod
    def branch_message_part(cls, part) -> List[str]:
        if not isinstance(part, str) and \
           hasattr(part, "__iter__"):
            return (str(p) for p in sorted(part))
        else:
            return [str(part)]

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
            wmflabs_prometheus:
                class: ores.metrics_collectors.Prometheus
        """
        logger.info("Loading Prometheus '{0}' from config.".format(name))

        return cls()
