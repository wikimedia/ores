"""
Class to implement PoolCounter lock manager.

This is useful to make sure too many connections are not coming from one IP.
"""

import logging
import socket
import hashlib

from .lock_manager import LockManager
from ..errors import TimeoutError, TooManyRequestsError

logger = logging.getLogger(__name__)


class PoolCounter(LockManager):
    def __init__(self, nodes):
        self.nodes = nodes
        self.stream = None

    def connect(self, key):
        hashes = []
        for node in self.nodes:
            hashes.append(
                (node, hashlib.sha256(bytes(node[0] + key, 'utf-8')).hexdigest())
            )
        node = sorted(hashes, key=lambda i: i[1])[0][0]
        try:
            self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self.stream.connect(node)
        except ConnectionRefusedError:
            logger.warning(
                'Can not connect to the PoolCounter node %s' % node[0])
            return False
        return True

    def lock(self, key, workers, maxqueue, timeout):
        if not self.stream:
            connected = self.connect(key)
            if not connected:
                return False
        try:
            self.stream.send(bytes(
                'ACQ4ME %s %d %d %d\n' % (key, workers, maxqueue, timeout),
                'utf-8'))
            data = self.stream.recv(4096).decode('utf-8')
        except socket.error as e:
            self.close()
            raise e

        if data.strip() == 'QUEUE_FULL':
            raise TooManyRequestsError

        if data.strip() == 'TIMEOUT':
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
        nodes = []
        for node in config[section_key][name]:
            nodes.append((node.split(':')[0],
                          int(node.split(':')[1])))

        return cls(nodes)
