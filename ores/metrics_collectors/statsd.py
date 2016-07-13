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

    def precache_request(self, context, model, version, duration):
        self.send_timing_event(('precache_request', context, model, version), duration)

    def scores_request(self, context, model, version, rev_id_count, duration):
        self.send_timing_event(('scores_request', context, model, version, rev_id_count), duration)
        self.send_increment_event(('revision_scored', context, model, version), count=rev_id_count)

    def datasources_extracted(self, context, model, version, rev_id_count, duration):
        self.send_timing_event(('datasources_extracted', context, model, version, rev_id_count), duration)

    def score_processed(self, context, model, version, duration):
        self.send_timing_event(('score_processed', context, model, version), duration)

    def score_processor_overloaded(self, context, model, version):
        self.send_increment_event(('score_processor_overloaded', context, model, version))

    def score_cache_hit(self, context, model, version):
        self.send_increment_event(('score_cache_hit', context, model, version))

    def score_errored(self, context, model, version):
        self.send_increment_event(('score_errored', context, model, version))

    def score_timed_out(self, context, model, version):
        self.send_increment_event(('score_timed_out', context, model, version))

    def send_timing_event(self, message_parts, duration_seconds):
        with self.statsd_client.pipeline() as pipe:
            for message in self.get_messages_from_parts(message_parts):
                pipe.timing(message, duration_seconds * 1000)

    def send_increment_event(self, message_parts, count=1):
        with self.statsd_client.pipeline() as pipe:
            for message in self.get_messages_from_parts(message_parts):
                pipe.incr(message, count=count)

    @classmethod
    def get_messages_from_parts(cls, message_parts):
        for i in range(len(message_parts)):
            yield '.'.join(['{}'] * (len(message_parts) - i)).format(*message_parts)

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
