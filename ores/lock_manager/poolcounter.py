"""
Class to implement PoolCounter lock manager.

This is useful to make sure too many connections are not coming from one IP.
"""

import socket

from .lock_manager import LockManager


class PoolCounter(LockManager):
    def __init__(self, config, logger):
        self.server = config['server']
        self.port = config['port']
        self.stream = None
        self.logger = logger

    def connect(self):
        self.stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        return self.stream.connect((self.server, self.port))

    def acq4me(self, key, workers, maxqueue, timeout):
        if not self.stream:
            self.connect()
        try:
            self.stream.send(bytes('ACQ4ME %s %d %d %d\n' % (key, workers, maxqueue, timeout), 'utf-8'))
            data = self.stream.recv(4096).decode('utf-8')
            print(data)
        except socket.error as e:
            self.stream = None
            raise e

        return data == 'LOCKED\n'

    def release(self, key):
        if not self.stream:
            self.connect()

        try:
            self.stream.send(bytes('RELEASE %s\n' % key, 'utf-8'))
            data = self.stream.recv(4096).decode('utf-8')
        except socket.error as e:
            self.stream = None
            raise e

        return data == 'RELEASED\n'

    def close(self):
        if self.stream:
            self.stream.close()
            self.stream = None
            return True
        else:
            return False

    def debug(self, message):
        self.logger.debug(message)
