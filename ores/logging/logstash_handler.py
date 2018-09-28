
from logging.handlers import DatagramHandler, SocketHandler
from .logstash_fomatter import LogstashFormatter


class LogstashHandler(DatagramHandler, SocketHandler):
    """
    Python logging handler for Logstash.

    :param host: The host of the logstash server.
    :param port: The port of the logstash server (default 5959).
    :param message_type: The type of the message (default logstash).
    :param tags: list of tags for a logger (default is None).
    """

    def __init__(self, host, port=5959, message_type='logstash', tags=None):
        super(LogstashHandler, self).__init__(host, port)
        self.formatter = LogstashFormatter(message_type, tags)

    def makePickle(self, record):
        return self.formatter.format(record)
