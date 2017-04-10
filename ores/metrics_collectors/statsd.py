import logging
import socket

from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class Statsd(MetricsCollector):
    """
    A metrics collector that uses :mod:`statsd` to connect to a graphite
    instance and send incr() and timing() events.
    """

    def __init__(self, statsd_client):
        self.statsd_client = statsd_client

    def precache_request(self, request, duration):
        self.send_timing_event('precache_request', request.context_name,
                               request.model_names, duration=duration)

    def scores_request(self, request, duration):
        self.send_timing_event('scores_request', request.context_name,
                               request.model_names, len(request.rev_ids),
                               duration=duration)
        self.send_increment_event('revision_scored', request.context_name,
                                  request.model_names,
                                  count=len(request.rev_ids))

    def datasources_extracted(self, request, rev_id_count, duration):
        self.send_timing_event('datasources_extracted', request.context_name,
                               request.model_names, rev_id_count,
                               duration=duration)

    def score_processed(self, request, duration):
        self.send_timing_event('score_processed', request.context_name,
                               request.model_names, duration=duration)

    def score_processor_overloaded(self, request):
        self.send_increment_event('score_processor_overloaded',
                                  request.context_name, request.model_names)

    def score_cache_hit(self, request, model_name):
        if request.precache:
            self.send_increment_event(
                'precache_cache_hit', request.context_name, model_name)
        else:
            self.send_increment_event(
                'score_cache_hit', request.context_name, model_name)

    def score_cache_miss(self, request, model_name):
        if request.precache:
            self.send_increment_event(
                'precache_cache_miss', request.context_name, model_name)
        else:
            self.send_increment_event(
                'score_cache_miss', request.context_name, model_name)

    def score_errored(self, request, model_name):
        self.send_increment_event('score_errored', request.context_name,
                                  model_name)

    def score_timed_out(self, request, duration):
        self.send_timing_event('score_timed_out', request.context_name,
                               request.model_names, duration=duration)

    def precache_score(self, request, duration):
        self.send_timing_event('precache_score', request.context_name,
                               request.model_names, duration=duration)

    def precache_scoring_error(self, request, status, duration):
        self.send_timing_event('precache_scoring_error', request.context_name,
                               request.model_names, status, duration=duration)

    def send_timing_event(self, *message_parts, duration=None):
        with self.statsd_client.pipeline() as pipe:
            for message in self.generate_messages(message_parts):
                pipe.timing(message, duration * 1000)

    def send_increment_event(self, *message_parts, count=1):
        with self.statsd_client.pipeline() as pipe:
            for message in self.generate_messages(message_parts):
                pipe.incr(message, count=count)

    @classmethod
    def generate_messages(cls, parts):
        """
        Performs a deterministic first walk of the tree implied by a list of
        message parts.

        generate_messages(["foo", "bar", ["herp", "derp"], "baz"]) yields:
        * "foo"
        * "foo.bar"
        * "foo.bar.herp"
        * "foo.bar.herp.baz"
        * "foo.bar.derp"
        * "foo.bar.derp.baz"
        """
        for message_parts in cls.generate_message_parts(parts):
            yield ".".join(message_parts)

    @classmethod
    def generate_message_parts(cls, parts, i=0, message=[]):
        if len(message) > 0:
            yield message

        if i < len(parts):
            for bpart in cls.branch_message_part(parts[i]):
                yield from cls.generate_message_parts(
                    parts, i=i + 1, message=message + [bpart])

    @classmethod
    def branch_message_part(cls, part):
        if not isinstance(part, str) and \
           hasattr(part, "__iter__"):
            return (str(p) for p in sorted(part))
        else:
            return [str(part)]

    @classmethod
    def from_parameters(cls, *args, **kwargs):
        import statsd
        statsd_client = statsd.StatsClient(*args, **kwargs)
        return cls(statsd_client)

    @classmethod
    def from_config(cls, config, name, section_key="metrics_collectors"):
        """
        metrics_collectors:
            wmflabs_statsd:
                class: ores.metrics_collectors.Statsd
                host: labmon1001.eqiad.wmnet
                prefix: ores.{hostname}
                maxudpsize: 512
        """
        logger.info("Loading Statsd '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = {k: v for k, v in section.items() if k != "class"}
        if 'prefix' in kwargs:
            kwargs['prefix'] = kwargs['prefix'] \
                               .format(hostname=socket.gethostname())
        return cls.from_parameters(**kwargs)
