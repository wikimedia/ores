import json
from logging import LogRecord

from ores.logging.logstash_fomatter import LogstashFormatter


def test_format():
    formatter = LogstashFormatter(tags=['ores'], host='ores.test.wmnet')
    log_record = LogRecord('test_ores', 2, '/dev/test/ores', 55, 'Log made',
                           [], None)
    formatted = json.loads(formatter.format(log_record).decode('utf-8'))
    formatted['@timestamp'] = '2018-09-28T11:34:56.507Z'

    assert formatted == {
        '@timestamp': '2018-09-28T11:34:56.507Z',
        '@version': '1',
        'exc_text': None,
        'host': 'ores.test.wmnet',
        'level': 'Level 2',
        'logger_name': 'test_ores',
        'message': 'Log made',
        'path': '/dev/test/ores',
        'tags': ['ores'],
        'type': 'ores'}


def test_format_source():
    formatted = LogstashFormatter.format_source('ores', 'ores.test.wmnet', 'scores/')

    assert formatted == 'ores://ores.test.wmnet/scores/'
