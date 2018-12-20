"""
Class to implement Redis task tracker.

This is useful to deduplicate celery jobs.
"""

import logging

from .task_tracker import TaskTracker

logger = logging.getLogger(__name__)
TTL = 5 * 60   # 5 minutes
PREFIX = "ores"


class RedisTaskTracker(TaskTracker):
    def __init__(self, redis, ttl=None, prefix=None):
        self.redis = redis
        self.ttl = int(ttl or TTL)
        self.prefix = str(prefix or PREFIX)

    def lock(self, key, value):
        return self.redis.setex(self.prefix + ':' + key, self.ttl,
                                bytes(value, 'utf-8'))

    def get_in_progress_task(self, key):
        value = self.redis.get(self.prefix + ':' + key)
        if value is None:
            return False
        else:
            return str(value, 'utf-8')

    def release(self, key):
        return self.redis.delete(self.prefix + ':' + key)

    @classmethod
    def from_parameters(cls, *args, ttl=None, prefix=None, **kwargs):
        try:
            import redis
        except ImportError:
            raise ImportError("Could not find redis-py.  This packages is " +
                              "required when using ores.lock_manager.Redis.")

        return cls(redis.StrictRedis(*args, **kwargs), ttl=ttl, prefix=prefix)

    @classmethod
    def from_config(cls, config, name, section_key="task_trackers"):
        """
        task_trackers:
            redis:
                class: ores.task_tracker.RedisTaskTracker
                host: localhost
                prefix: ores-derp
                ttl: 9001
        """
        logger.info("Loading Redis '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = {k: v for k, v in section.items() if k != "class"}

        return cls.from_parameters(**kwargs)
