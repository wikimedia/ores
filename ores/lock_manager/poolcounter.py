"""
Class to implement PoolCounter lock manager.

This is useful to make sure too many connections are not coming from one IP.
"""

import logging
import socket

from .lock_manager import LockManager
from ..errors import TimeoutError

logger = logging.getLogger(__name__)


class PoolCounter(LockManager):
    def __init__(self, primary_node, secondary_node=None):
        self.primary_node = primary_node
        self.secondary_node = secondary_node
        self.stream = None

    def connect(self):
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        try:
            self.stream.connect(self.primary_node)
        except ConnectionRefusedError:
            if self.secondary_node:
                logger.warning(
                    'Can not connect to the primary PoolCounter node, '
                    'falling back to the secondary node')
                self.stream.connect(self.secondary_node)
            else:
                raise

    def lock(self, key, workers, maxqueue, timeout):
        if not self.stream:
            self.connect()
        try:
            self.stream.send(bytes(
                'ACQ4ME %s %d %d %d\n' % (key, workers, maxqueue, timeout),
                'utf-8'))
            data = self.stream.recv(4096).decode('utf-8')
        except socket.error as e:
            self.close()
            raise e

        if data.strip() in ['TIMEOUT', 'QUEUE_FULL']:
            raise TimeoutError

        return data.strip() == 'LOCKED'

    def release(self, key):
        if not self.stream:
            return False

        try:
            self.stream.send(bytes('RELEASE %s\n' % key, 'utf-8'))
            data = self.stream.recv(4096).decode('utf-8')
        except socket.error as e:
            self.close()
            raise e

        return data.strip() == 'RELEASED'

    def close(self):
        if self.stream:
            self.stream.close()
            self.stream = None
            return True

        return False

    @classmethod
    def from_config(cls, config, name, section_key="lock_managers"):
        primary_node_config = config[section_key][name]['primary_node']
        secondary_node_config = config[section_key][name].get('secondary_node')
        if secondary_node_config:
            secondary_node = (secondary_node_config['server'],
                              secondary_node_config['port'])
        else:
            secondary_node = None
        return cls(
            (primary_node_config['server'], primary_node_config['port']),
            secondary_node
        )
