import json
import logging
from hashlib import sha1

from .score_cache import ScoreCache

logger = logging.getLogger("ores.score_caches.redis")

TTL = 60 * 60 * 24 * 365 * 16  # 16 years
PREFIX = "ores"


class Redis(ScoreCache):

    def __init__(self, redis, ttl=None, prefix=None):
        self.redis = redis
        self.ttl = int(ttl or TTL)
        self.prefix = str(prefix or PREFIX)

    def lookup(self, context_name, model_name, rev_id, version=None,
               injection_cache=None):
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
        key = self._generate_key(
            context_name, model_name, rev_id, version=version,
            injection_cache=injection_cache)

        logger.debug("Storing score at {0}".format(key))
        self.redis.setex(key, self.ttl, bytes(json.dumps(score), 'utf-8'))

    def _generate_key(self, wiki, model, rev_id, version=None,
                      injection_cache=None):
        if injection_cache is None or len(injection_cache) == 0:
            key_values = [self.prefix, wiki, model, rev_id, version]
        else:
            cache_hash = self.hash_cache(injection_cache)
            key_values = [self.prefix, wiki, model, rev_id, version,
                          cache_hash]

        return ":".join(str(v) for v in key_values)

    @classmethod
    def from_parameters(cls, *args, ttl=None, prefix=None, **kwargs):
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
        sorted_tuple = tuple(sorted(cache.items()))
        return sha1(bytes(str(sorted_tuple), 'utf8')).hexdigest()
