import json

import redis

from .cache import Cache


class Redis(Cache):

    def __init__(self, redis, prefix=""):
        self.redis = redis
        self.prefix = str(prefix)

    def lookup(self, wiki, model, rev_id):
        wiki = str(wiki)
        model = str(model)
        rev_id = str(rev_id)
        try:
            value = self.redis.get(":".join([self.prefix, wiki, model, rev_id]))
            return json.loads(value)
        except KeyError:
            return None

    def store(self, wiki, model, rev_id, score):
        wiki = str(wiki)
        model = str(model)
        rev_id = str(rev_id)
        score = json.dumps(score)

        self.redis.put(":".join([self.prefix, wiki, model, rev_id],
                       score)

    @classmethod
    def from_parameters(cls, host, port, prefix=""):
        return cls(redis.connect(host=host, port=port), prefix=prefix)
