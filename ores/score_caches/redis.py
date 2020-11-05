import json
import logging
from hashlib import sha1

from .score_cache import ScoreCache

logger = logging.getLogger("ores.score_caches.redis")
sentinel_logger = logging.getLogger('ores.score_caches.RedisSentinel')

TTL = 60 * 60 * 24 * 365 * 16  # 16 years
PREFIX = "ores"
CLUSTER = 'orescache'
SOCKET_TIMEOUT = 0.1


class Redis(ScoreCache):

    def __init__(self, redis, ttl=None, prefix=None):
        """
        Initialize redis instance.

        Args:
            self: (todo): write your description
            redis: (todo): write your description
            ttl: (int): write your description
            prefix: (str): write your description
        """
        self.redis = redis
        self.ttl = int(ttl or TTL)
        self.prefix = str(prefix or PREFIX)

    def lookup(self, context_name, model_name, rev_id, version=None,
               injection_cache=None):
        """
        Retrieves a model object.

        Args:
            self: (todo): write your description
            context_name: (str): write your description
            model_name: (str): write your description
            rev_id: (int): write your description
            version: (str): write your description
            injection_cache: (todo): write your description
        """
        key = self._generate_key(
            context_name, model_name, rev_id, version=version,
            injection_cache=injection_cache)

        logger.debug("Looking up score at {0}".format(key))
        value = self.redis.get(key)
        if value is None:
            raise KeyError(key)
        else:
            return json.loads(str(value, 'utf-8'))

    def store(self, score, context_name, model_name, rev_id, version=None,
              injection_cache=None):
        """
        Store a credential in the cache.

        Args:
            self: (todo): write your description
            score: (todo): write your description
            context_name: (str): write your description
            model_name: (str): write your description
            rev_id: (str): write your description
            version: (str): write your description
            injection_cache: (todo): write your description
        """
        key = self._generate_key(
            context_name, model_name, rev_id, version=version,
            injection_cache=injection_cache)

        logger.debug("Storing score at {0}".format(key))
        self.redis.setex(key, self.ttl, bytes(json.dumps(score), 'utf-8'))

    def _generate_key(self, wiki, model, rev_id, version=None,
                      injection_cache=None):
        """
        Generate a cache key.

        Args:
            self: (todo): write your description
            wiki: (int): write your description
            model: (todo): write your description
            rev_id: (str): write your description
            version: (str): write your description
            injection_cache: (int): write your description
        """
        if injection_cache is None or len(injection_cache) == 0:
            key_values = [self.prefix, wiki, model, rev_id, version]
        else:
            cache_hash = self.hash_cache(injection_cache)
            key_values = [self.prefix, wiki, model, rev_id, version,
                          cache_hash]

        return ":".join(str(v) for v in key_values)

    @classmethod
    def from_parameters(cls, *args, ttl=None, prefix=None, **kwargs):
        """
        Creates a new instance from a redis instance.

        Args:
            cls: (todo): write your description
            ttl: (todo): write your description
            prefix: (str): write your description
        """
        try:
            import redis
        except ImportError:
            raise ImportError("Could not find redis-py.  This packages is " +
                              "required when using ores.score_caches.Redis.")

        return cls(redis.StrictRedis(*args, **kwargs), ttl=ttl, prefix=prefix)

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        """
        score_caches:
            redis_cache:
                class: ores.score_caches.Redis
                host: localhost
                prefix: ores-derp
                ttl: 9001
        """
        logger.info("Loading Redis '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = {k: v for k, v in section.items() if k != "class"}

        return cls.from_parameters(**kwargs)

    @classmethod
    def hash_cache(cls, cache):
        """
        Return a hash of the cache.

        Args:
            cls: (todo): write your description
            cache: (dict): write your description
        """
        sorted_tuple = tuple(sorted(cache.items()))
        return sha1(bytes(str(sorted_tuple), 'utf8')).hexdigest()


class RedisSentinel(ScoreCache):

    def __init__(self, sentinel, ttl=None, prefix=None, cluster=None, socket_timeout=None):
        """
        Initialize the socket.

        Args:
            self: (todo): write your description
            sentinel: (todo): write your description
            ttl: (int): write your description
            prefix: (str): write your description
            cluster: (str): write your description
            socket_timeout: (float): write your description
        """
        self.sentinel = sentinel
        self.ttl = int(ttl or TTL)
        self.prefix = str(prefix or PREFIX)
        self.cluster = str(cluster or CLUSTER)
        self.socket_timeout = float(socket_timeout or SOCKET_TIMEOUT)

    def lookup(self, context_name, model_name, rev_id, version=None,
               injection_cache=None):
        """
        Execute a lookup.

        Args:
            self: (todo): write your description
            context_name: (str): write your description
            model_name: (str): write your description
            rev_id: (int): write your description
            version: (str): write your description
            injection_cache: (todo): write your description
        """
        key = self._generate_key(
            context_name, model_name, rev_id, version=version,
            injection_cache=injection_cache)

        replica = self.sentinel.slave_for(self.cluster, socket_timeout=self.socket_timeout)
        sentinel_logger.debug("Looking up score at {0} in replica".format(key))
        value = replica.get(key)
        if value is None:
            raise KeyError(key)
        else:
            return json.loads(str(value, 'utf-8'))

    def store(self, score, context_name, model_name, rev_id, version=None,
              injection_cache=None):
        """
        Store a master in - value pair.

        Args:
            self: (todo): write your description
            score: (todo): write your description
            context_name: (str): write your description
            model_name: (str): write your description
            rev_id: (str): write your description
            version: (str): write your description
            injection_cache: (todo): write your description
        """
        key = self._generate_key(
            context_name, model_name, rev_id, version=version,
            injection_cache=injection_cache)

        master = self.sentinel.master_for(self.cluster, socket_timeout=self.socket_timeout)
        sentinel_logger.debug("Storing score at {0} in master".format(key))
        master.setex(key, self.ttl, bytes(json.dumps(score), 'utf-8'))

    def _generate_key(self, wiki, model, rev_id, version=None,
                      injection_cache=None):
        """
        Generate a cache key for a given wiki.

        Args:
            self: (todo): write your description
            wiki: (int): write your description
            model: (todo): write your description
            rev_id: (str): write your description
            version: (str): write your description
            injection_cache: (int): write your description
        """
        if injection_cache is None or len(injection_cache) == 0:
            key_values = [self.prefix, wiki, model, rev_id, version]
        else:
            cache_hash = Redis.hash_cache(injection_cache)
            key_values = [self.prefix, wiki, model, rev_id, version,
                          cache_hash]

        return ":".join(str(v) for v in key_values)

    @classmethod
    def from_parameters(cls, hosts, ttl=None, prefix=None, cluster=None,
                        socket_timeout=None):
        """
        Create a new : class from a redis instance.

        Args:
            cls: (todo): write your description
            hosts: (list): write your description
            ttl: (todo): write your description
            prefix: (str): write your description
            cluster: (todo): write your description
            socket_timeout: (todo): write your description
        """
        try:
            from redis.sentinel import Sentinel
        except ImportError:
            raise ImportError("Could not find redis-py.  This packages is " +
                              "required when using ores.score_caches.RedisSentinel.")

        hosts = [i.split(':') for i in hosts]
        return cls(Sentinel(hosts, socket_timeout=socket_timeout),
                   ttl=ttl, prefix=prefix, cluster=cluster,
                   socket_timeout=socket_timeout)

    @classmethod
    def from_config(cls, config, name, section_key="score_caches"):
        """
        score_caches:
            redis_sentinel:
                class: ores.score_caches.RedisSentinel
                prefix: ores-derp
                ttl: 9001
                socket_timeout: 0.1
                cluster: mymaster
                hosts:
                  - localhost:5000
                  - localhost:5001
                  - localhost:5002
        """
        sentinel_logger.info("Loading RedisSentinel '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = {k: v for k, v in section.items() if k != "class"}

        return cls.from_parameters(**kwargs)
