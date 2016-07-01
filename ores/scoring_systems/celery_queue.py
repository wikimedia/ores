import logging
import re
from urllib.parse import urlparse
from itertools import chain

import celery
import celery.exceptions
import mwapi.errors
import revscoring.errors
from celery.signals import before_task_publish

from ..errors import TimeoutError, ScoreProcessorOverloaded
from .scoring_system import ScoringSystem

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


class CeleryQueue(ScoringSystem):

    def __init__(self, *args, application, queue_maxsize=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application
        self.queue_maxsize = int(queue_maxsize) if queue_maxsize is not None \
                             else None

        self.redis = redis_from_url(self.application.conf.BROKER_URL)

        if self.queue_maxsize is not None and self.redis is None:
            logger.warning("No redis connection.  Can't check queue size")

        expected_errors = (revscoring.errors.RevisionNotFound,
                           revscoring.errors.PageNotFound,
                           revscoring.errors.UserNotFound,
                           revscoring.errors.DependencyError,
                           mwapi.errors.RequestError,
                           mwapi.errors.TimeoutError,
                           TimeoutError)

        @self.application.task(throws=expected_errors,
                               queue=DEFAULT_CELERY_QUEUE,
                               priority=0)
        def _lookup_score_in_map(result_id, model_name):
            score_map_result = self._process_score_map.AsyncResult(result_id)
            score_map = score_map_result.get(timeout=self.timeout)
            return score_map[model_name]

        @self.application.task(throws=expected_errors,
                               queue=DEFAULT_CELERY_QUEUE,
                               priority=0)
        def _process_score_map(
             context_name, model_names, rev_id, root_cache=None,
             injection_cache=None, include_features=False):
            score_map = ScoringSystem._process_score_map(
                self, context_name, model_names, rev_id, root_cache=root_cache,
                injection_cache=injection_cache,
                include_features=include_features)
            return score_map

        APPLICATIONS.append(application)

        self._process_score_map = _process_score_map
        self._lookup_score_in_map = _lookup_score_in_map

    def _process_missing_scores(self, context_name, missing_model_set_revs,
                                root_caches, injection_caches,
                                include_features, inprogress_results=None):
        context = self[context_name]

        inprogress_results = inprogress_results or {}

        # Generate score results
        results = {}
        for missing_models, rev_ids in missing_model_set_revs.items():
            for rev_id in rev_ids:
                root_cache = root_caches[rev_id]
                injection_cache = injection_caches.get(rev_id) \
                                  if injection_caches is not None else None
                result = self._process_score_map.delay(
                    context_name, missing_models, rev_id, root_cache,
                    injection_cache=injection_cache,
                    include_features=include_features)

                for model_name in missing_models:
                    task_id = context.format_id_string(
                        model_name, rev_id, injection_cache=injection_cache)
                    score_result = self._lookup_score_in_map.apply_async(
                        args=(result.id, model_name), task_id=task_id)
                    if rev_id in results:
                        results[rev_id][model_name] = score_result
                    else:
                        results[rev_id] = {model_name: score_result}

        # Read results
        rev_scores = {}
        errors = {}
        combined_results = chain(inprogress_results.items(), results.items())
        for rev_id, model_results in combined_results:
            if rev_id not in rev_scores:
                rev_scores[rev_id] = {}
            for model_name, score_result in model_results.items():
                try:
                    rev_scores[rev_id][model_name] = \
                        score_result.get(timeout=self.timeout)
                except celery.exceptions.TimeoutError:
                    errors[rev_id] = TimeoutError(
                        "Timed out after {0} seconds.".format(self.timeout))
                except Exception as error:
                    if rev_id in errors:
                        errors[rev_id][model_name] = error
                    else:
                        errors[rev_id] = {model_name: error}

        return rev_scores, errors

    def _lookup_inprogress_results(self, context_name, model_names, rev_ids,
                                   injection_caches=None, rev_scores=None):
        context = self[context_name]

        rev_scores = rev_scores or {}
        for rev_id in rev_ids:
            injection_cache = injection_caches.get(rev_id) \
                              if injection_caches is not None else None

            for model_name in model_names:
                if rev_id in rev_scores and \
                   model_name in rev_scores[rev_id]:
                    continue

                task_id = context.format_id_string(
                    model_name, rev_id, injection_cache=injection_cache)
                score_result = \
                    self._lookup_score_in_map.AsyncResult(task_id)
                if score_result.state in ("REQUESTED", "SENT", "STARTED",
                                          "SUCCESS"):
                    logger.info("Found in-progress result for {0} -- {1}"
                                .format(task_id, score_result.state))
                    if rev_id in rev_scores:
                        rev_scores[rev_id][model_name] = score_result
                    else:
                        rev_scores[rev_id] = {model_name: score_result}

        return rev_scores

    def _register_model_set_revs_to_process(self, context_name, model_set_revs,
                                            injection_caches):
        context = self[context_name]

        for model_set, rev_ids in model_set_revs.items():
            for rev_id in rev_ids:
                for model_name in model_set:
                    injection_cache = injection_caches.get(rev_id) \
                                      if injection_caches is not None else None
                    task_id = context.format_id_string(
                        model_name, rev_id, injection_cache=injection_cache)
                    self.application.backend.store_result(
                        task_id, {}, 'REQUESTED')

    def _score(self, *args, **kwargs):
        self._check_queue_full()
        return super()._score(*args, **kwargs)

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
                raise ScoreProcessorOverloaded(message)

    @classmethod
    def _build_context_map(cls, config, name, section_key="scoring_systems"):
        from .. import ores
        from ..scoring_context import ScoringContext, ClientScoringContext

        section = config[section_key][name]

        if hasattr(ores, "_is_wsgi_client") and ores._is_wsgi_client:
            ScoringContextClass = ClientScoringContext
        else:
            ScoringContextClass = ScoringContext

        return {name: ScoringContextClass.from_config(config, name)
                for name in section['scoring_contexts']}

    @classmethod
    def from_config(cls, config, name, section_key="scoring_systems"):
        logger.info("Loading CeleryQueue '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = cls._kwargs_from_config(
            config, name, section_key=section_key)
        queue_maxsize = section.get('queue_maxsize')
        application = celery.Celery(__name__)
        application.conf.update(**{k: v for k, v in section.items()
                                   if k not in ('class', 'context_map',
                                                'score_cache',
                                                'metrics_collector', 'timeout',
                                                'queue_maxsize')})
        application.conf.CELERY_CREATE_MISSING_QUEUES = True

        return cls(application=application,
                   queue_maxsize=queue_maxsize, **kwargs)


PASS_HOST_PORT = re.compile(
    r"((?P<password>[^@]+)@)?" +
    r"(?P<host>[^:]+)?" +
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
