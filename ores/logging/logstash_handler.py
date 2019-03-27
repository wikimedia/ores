from logging.handlers import DatagramHandler

from .logstash_fomatter import LogstashFormatter


class LogstashHandler(DatagramHandler):
    """
    Python logging handler for Logstash.

    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 12201).
    :param tags: list of tags for a logger (default is None).
    """

    def __init__(self, host, port=12201, tags=None):
        super(LogstashHandler, self).__init__(host, port)
        self.formatter = LogstashFormatter(tags=tags)

    def makePickle(self, record):
        return self.formatter.format(record)
