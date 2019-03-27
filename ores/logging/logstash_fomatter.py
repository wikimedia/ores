import json
import logging
import socket
import traceback
from datetime import datetime, timezone


class LogstashFormatter(logging.Formatter):
    # The list contains all the attributes listed in
    # http://docs.python.org/library/logging.html#logrecord-attributes
    skip_list = (
        'args', 'asctime', 'created', 'exc_info', 'filename', 'funcName',
        'levelname', 'levelno', 'lineno', 'message', 'module', 'msecs',
        'msg', 'name', 'pathname', 'process', 'processName',
        'relativeCreated', 'stack_info', 'thread', 'threadName')
    easy_types = (str, bool, dict, float, int, list, type(None))

    def __init__(self, tags=None, host=None):
        self.tags = tags if tags is not None else []
        self.host = host if host is not None else socket.gethostname()

    def format(self, record):
        # Create message dict
        message = {
            '@timestamp': self.format_timestamp(record.created),
            '@version': '1',
            'message': record.getMessage(),
            'host': self.host,
            'path': record.pathname,
            'tags': self.tags,
            'type': 'ores',

            # Extra Fields
            'level': record.levelname,
            'logger_name': record.name,
        }

        # Add extra fields
        message.update(self.get_extra_fields(record))

        # If exception, add debug info
        if record.exc_info:
            message.update(self.get_debug_fields(record))

        return self.serialize(message)

    def get_extra_fields(self, record):
        fields = {}

        for key, value in record.__dict__.items():
            if key not in LogstashFormatter.skip_list:
                if isinstance(value, LogstashFormatter.easy_types):
                    fields[key] = value
                else:
                    fields[key] = repr(value)

        return fields

    def get_debug_fields(self, record):
        return {
            'stack_trace': self.format_exception(record.exc_info),
            'lineno': record.lineno,
            'process': record.process,
            'thread_name': record.threadName,
            'funcName': record.funcName,
            'processName': record.processName,
        }

    @classmethod
    def format_source(cls, message_type, host, path):
        return "%s://%s/%s" % (message_type, host, path)

    @classmethod
    def format_timestamp(cls, time):
        tstamp = datetime.fromtimestamp(time, timezone.utc)
        return tstamp.isoformat()

    @classmethod
    def format_exception(cls, exc_info):
        return ''.join(traceback.format_exception(*exc_info)) if exc_info else ''

    @classmethod
    def serialize(cls, message):
        return bytes(json.dumps(message) + '\n', 'utf-8')
