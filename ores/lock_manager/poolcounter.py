"""
Class to implement PoolCounter lock manager.

This is useful to make sure too many connections are not coming from one IP.
"""

import socket

from .lock_manager import LockManager


class PoolCounter(LockManager):
    def __init__(self, config):
        self.server = config['server']
        self.port = config['port']
        self.stream = None

    def connect(self):
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        return self.stream.connect((self.server, self.port))

    def lock(self, key, workers, maxqueue, timeout):
        if not self.stream:
            self.connect()
        try:
            self.stream.send(bytes('ACQ4ME %s %d %d %d\n' % (key, workers, maxqueue, timeout), 'utf-8'))
            data = self.stream.recv(4096).decode('utf-8')
        except socket.error as e:
            self.close()
            raise e

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
        else:
            return False
