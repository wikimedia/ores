import logging
import re
from hashlib import sha1
from urllib.parse import urlparse

import celery
import mwapi.errors
import revscoring.errors
from celery.signals import before_task_publish

from .. import errors
from ..metrics_collectors import MetricsCollector
from ..score_caches import ScoreCache
from ..util import jsonify_error
from .timeout import Timeout, TimeoutError

logger = logging.getLogger(__name__)

APPLICATIONS = []

DEFAULT_CELERY_QUEUE = "celery"


@before_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):

    for application in APPLICATIONS:
        task = application.tasks.get(sender)
        backend = task.backend if task else application.backend

        logger.debug("Setting state to 'SENT' for {0}".format(body['id']))
        backend.store_result(body['id'], result=None, status="SENT")


class Celery(Timeout):

    def __init__(self, *args, application, queue_maxsize=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application
        self.queue_maxsize = int(queue_maxsize) if queue_maxsize is not None \
                             else None

        self.redis = redis_from_url(self.application.conf.BROKER_URL)

        if self.queue_maxsize is not None and self.redis is None:
            logger.warning("No redis connection.  Can't check queue size")

        expected_errors = (revscoring.errors.RevisionNotFound,
                           revscoring.errors.DependencyError,
                           mwapi.errors.RequestError,
                           mwapi.errors.TimeoutError,
                           TimeoutError)

        @self.application.task(throws=expected_errors,
                               queue=DEFAULT_CELERY_QUEUE)
        def _process_task(context, model, cache, include_features):
            return Timeout._process(self, context, model, cache=cache,
                                    include_features=include_features)

        @self.application.task(throws=expected_errors,
                               queue=DEFAULT_CELERY_QUEUE)
        def _score_revision_task(context, model, rev_id, cache=None,
                                 include_features=False):
            return Timeout._score_revision(self, context, model, rev_id,
                                           cache=cache,
                                           include_features=include_features)

        APPLICATIONS.append(application)

        self._process_task = _process_task

        self._score_revision_task = _score_revision_task

    def _score_in_celery(self, context, model, rev_ids, caches,
                         include_features):
        scores = {}
        feature_maps = {}
        results = {}

        if len(rev_ids) == 0:
            return scores, feature_maps
        if len(rev_ids) == 1:  # Special case -- do everything in celery
            rev_id = rev_ids.pop()
            cache = (caches or {}).get(rev_id, {})
            id_string = self._generate_id(context, model, rev_id, cache)
            result = self._score_revision_task.apply_async(
                args=(context, model, rev_id),
                kwargs={'include_features': include_features, 'cache': cache},
                task_id=id_string
            )
            results[rev_id] = result
        else:  # Otherwise, try and batch
            # Get the root datasources for the rest of the batch (IO)
            root_ds_caches = self._get_root_ds(context, model, rev_ids,
                                               caches=caches)

            # Extract features and generate scores (CPU)
            for rev_id, (error, cache) in root_ds_caches.items():
                if error is not None:
                    scores[rev_id] = {'error': jsonify_error(error)}
                else:
                    injection_cache = (caches or {}).get(rev_id)
                    id_string = \
                        self._generate_id(context, model, rev_id,
                                          injection_cache)
                    result = self._process_task.apply_async(
                        args=(context, model, cache, include_features),
                        task_id=id_string
                    )
                    results[rev_id] = result

        # Process async results
        for rev_id, result in results.items():
            try:
                score, feature_vals = result.get(self.timeout)
                if feature_vals is not None:
                    feature_maps[rev_id] = feature_vals
                scores[rev_id] = score
                cache = (caches or {}).get(rev_id, {})
                self._store(context, model, rev_id, score, cache)
            except Exception as error:
                scores[rev_id] = {'error': jsonify_error(error)}

        return scores, feature_maps

    def _generate_id(self, context, model, rev_id, cache):
        scorer_model = self[context][model]
        version = scorer_model.version

        id_string = ":".join(str(v) for v in [context, model, rev_id, version])

        if cache is None or len(cache) == 0:
            return id_string
        else:
            cache_hash = self.hash_cache(cache)
            return id_string + ":" + cache_hash

    def _check_queue_full(self):
        # Check redis to see if the queue of waiting tasks is too big.
        # This is a hack to implement backpressure because celery doesn't
        # support it natively.
        # This will result in a race condition, but it should have OK
        # properties.
        if self.redis is not None:
            queue_size = self.redis.llen(DEFAULT_CELERY_QUEUE)
            if queue_size > self.queue_maxsize:
                message = "Queue size is too full {0}".format(queue_size)
                logger.warning(message)
                raise errors.ScoreProcessorOverloaded(message)

    def _score(self, context, model, rev_ids, caches=None,
               include_features=False):
        scores = {}
        feature_maps = {}
        self._check_queue_full()  # Raises ScoreProcessorOverloaded

        rev_ids = set(rev_ids)

        if not include_features:
            # Lookup scoring results that are currently in progress
            results = self._lookup_inprogress_results(context, model, rev_ids,
                                                      caches)
            missing_ids = rev_ids - results.keys()

            # Lookup scoring results that are in the cache
            scores = self._lookup_cached_scores(context, model, missing_ids,
                                                caches)
            missing_ids = missing_ids - scores.keys()
        else:
            results = {}
            missing_ids = rev_ids

        # Generate scores for missing rev_ids
        new_scores, new_feature_maps = \
            self._score_in_celery(context, model, missing_ids,
                                  caches=caches,
                                  include_features=include_features)
        scores.update(new_scores)
        feature_maps.update(new_feature_maps)

        # Gather results
        for rev_id in results:
            try:
                scores[rev_id], feature_maps[rev_id] = \
                    results[rev_id].get(self.timeout)
            except Exception as error:
                scores[rev_id] = {'error': jsonify_error(error)}

        # Return scores
        return scores, feature_maps

    def _lookup_inprogress_results(self, context, model, rev_ids, caches):
        scorer_model = self[context][model]
        version = scorer_model.version

        results = {}
        for rev_id in rev_ids:
            cache = (caches or {}).get(rev_id, {})
            id_string = self._generate_id(context, model, rev_id, cache)
            try:
                results[rev_id] = self._get_result(id_string)
                self.metrics_collector.score_cache_hit(context, model, version)
            except KeyError:
                pass

        return results

    def _get_result(self, id_string):

        # Try to get an async_result for an in_progress task
        result = self._score_revision_task.AsyncResult(task_id=id_string)
        logger.debug("Checking if {0} is already being processed [{1}]"
                     .format(repr(id_string), result.state))
        if result.state not in ("SENT", "STARTED", "SUCCESS"):
            raise KeyError(id_string)
        else:
            logger.debug("Found AsyncResult for {0}".format(repr(id_string)))
            return result

    @classmethod
    def hash_cache(cls, cache):
        sorted_tuple = tuple(sorted(cache.items()))
        return sha1(bytes(str(sorted_tuple), 'utf8')).hexdigest()

    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):
        logger.info("Loading Celery '{0}' from config.".format(name))
        from ..scoring_contexts import ScoringContext

        section = config[section_key][name]

        scoring_contexts = {name: ScoringContext.from_config(config, name)
                            for name in section['scoring_contexts']}

        if 'score_cache' in section:
            score_cache = ScoreCache.from_config(config, section['score_cache'])
        else:
            score_cache = None

        if 'metrics_collector' in section:
            metrics_collector = \
                MetricsCollector.from_config(config,
                                             section['metrics_collector'])
        else:
            metrics_collector = None

        timeout = section.get('timeout')
        queue_maxsize = section.get('queue_maxsize')
        application = celery.Celery('ores.score_processors.celery')
        application.conf.update(**{k: v for k, v in section.items()
                                   if k not in ('class', 'timeout',
                                                'queue_maxsize')})
        application.conf.CELERY_CREATE_MISSING_QUEUES = True

        return cls(scoring_contexts, application=application, timeout=timeout,
                   score_cache=score_cache, queue_maxsize=queue_maxsize,
                   metrics_collector=metrics_collector)


PASS_HOST_PORT = re.compile(
    r"(?:\:(?P<password>[^@]+)@)?"
    r"(?P<host>[^:]+)?"
    r"(:(?P<port>[0-9]+))?"
)
"""
Matches <password>@<host>:<port>
"""


def redis_from_url(url):
    """
    Converts a redis URL used by celery into a `redis.Redis` object.
    """
    # Makes sure that we only try to import redis when we need
    # to use it
    import redis

    url = url or ""
    parsed_url = urlparse(url)
    if parsed_url.scheme != "redis":
        return None

    kwargs = {}
    match = PASS_HOST_PORT.match(parsed_url.netloc)
    if match.group('password') is not None:
        kwargs['password'] = match.group('password')
    if match.group('host') is not None:
        kwargs['host'] = match.group('host')
    if match.group('port') is not None:
        kwargs['port'] = int(match.group('port'))

    if len(parsed_url.path) > 1:
        # Removes "/" from the beginning
        kwargs['db'] = int(parsed_url.path[1:])

    return redis.StrictRedis(**kwargs)
