import json
import logging

from .score_cache import ScoreCache

logger = logging.getLogger("ores.score_caches.redis")

TTL = 60 * 60 * 24 * 365 * 16  # 16 years
PREFIX = "ores"


class Redis(ScoreCache):

    def __init__(self, redis, ttl=None, prefix=None):
        self.redis = redis
        self.ttl = int(ttl or TTL)
        self.prefix = str(prefix or PREFIX)

    def lookup(self, wiki, model, rev_id, version=None):
        wiki = str(wiki)
        model = str(model)
        rev_id = str(rev_id)
        version = str(version)

        key = ":".join([self.prefix, wiki, model, rev_id, version])
        logger.debug("Looking up score at {0}".format(key))
        value = self.redis.get(key)
        if value is None:
            raise KeyError(key)
        else:
            return json.loads(str(value, 'utf-8'))

    def store(self, wiki, model, rev_id, score, version=None):
        wiki = str(wiki)
        model = str(model)
        rev_id = str(rev_id)
        version = str(version)

        key = ":".join([self.prefix, wiki, model, rev_id, version])
        logger.debug("Storing score at {0}".format(key))

        self.redis.setex(key, self.ttl, bytes(json.dumps(score), 'utf-8'))

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
