import logging
import re
from itertools import chain
from urllib.parse import urlparse

import celery
import celery.exceptions
import celery.states
import mwapi.errors
import revscoring.errors
from celery.signals import before_task_publish

from .. import errors
from .scoring_system import ScoringSystem

logger = logging.getLogger(__name__)

_applications = []

DEFAULT_CELERY_QUEUE = "celery"
SENT = "SENT"
REQUESTED = "REQUESTED"


@before_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    for application in _applications:
        task = application.tasks.get(sender)
        backend = task.backend if task else application.backend

        logger.debug("Setting state to {0} for {1}".format(SENT, body['id']))
        backend.store_result(body['id'], result=None, status=SENT)


class CeleryQueue(ScoringSystem):

    def __init__(self, *args, application, queue_maxsize=None, **kwargs):
        super().__init__(*args, **kwargs)
        global _applications
        self.application = application
        self.queue_maxsize = int(queue_maxsize) if queue_maxsize is not None \
                             else None

        self.redis = redis_from_url(self.application.conf.BROKER_URL)

        if self.queue_maxsize is not None and self.redis is None:
            logger.warning("No redis connection.  Can't check queue size")

        self._initialize_tasks()

        _applications.append(application)

    def _initialize_tasks(self):
        expected_errors = (revscoring.errors.RevisionNotFound,
                           revscoring.errors.PageNotFound,
                           revscoring.errors.UserNotFound,
                           revscoring.errors.DependencyError,
                           mwapi.errors.RequestError,
                           mwapi.errors.TimeoutError,
                           errors.TimeoutError)

        @self.application.task(throws=expected_errors,
                               queue=DEFAULT_CELERY_QUEUE)
        def _process_score_map(request, model_names, rev_id, root_cache):
            logger.info("Generating a score map for {0}"
                        .format(request.format(rev_id, model_names)))

            score_map = ScoringSystem._process_score_map(
                self, request, rev_id, model_names,
                root_cache=root_cache)

            logger.info("Completed generating score map for {0}"
                        .format(request.format(rev_id, model_names)))
            return score_map

        @self.application.task(throws=expected_errors,
                               queue=DEFAULT_CELERY_QUEUE)
        def _lookup_score_in_map(result_id, model_name):
            logger.info("Looking up {0} in {1}".format(model_name, result_id))
            score_map_result = self._process_score_map.AsyncResult(result_id)
            try:
                score_map = score_map_result.get(timeout=self.timeout)

            except celery.exceptions.TimeoutError:
                raise errors.TimeoutError(
                    "Timed out after {0} seconds.".format(self.timeout))
            logger.info("Found {0} in {1}!".format(model_name, result_id))
            return score_map[model_name]

        self._process_score_map = _process_score_map
        self._lookup_score_in_map = _lookup_score_in_map

    def _process_missing_scores(self, request, missing_model_set_revs,
                                root_caches, inprogress_results=None):
        logger.debug("Processing missing scores {0}:{1}."
                     .format(request.context_name, missing_model_set_revs))
        context = self[request.context_name]

        inprogress_results = inprogress_results or {}

        # Generate score results
        results = {}
        for missing_models, rev_ids in missing_model_set_revs.items():
            for rev_id in rev_ids:
                injection_cache = request.injection_caches.get(rev_id)
                if rev_id not in root_caches:
                    for model_name in missing_models:
                        task_id = context.format_id_string(
                            model_name, rev_id, injection_cache=injection_cache)
                        self.application.backend.mark_as_failure(
                            task_id, RuntimeError("Never started"))
                    continue
                root_cache = {str(k): v for k, v in root_caches[rev_id].items()}
                result = self._process_score_map.delay(
                    request, missing_models, rev_id, root_cache)

                for model_name in missing_models:
                    task_id = context.format_id_string(
                        model_name, rev_id, injection_cache=injection_cache)
                    score_result = self._lookup_score_in_map.apply_async(
                        args=(result.id, model_name), task_id=task_id,
                        expires=self.timeout)
                    if rev_id in results:
                        results[rev_id][model_name] = score_result
                    else:
                        results[rev_id] = {model_name: score_result}

        # Read results
        rev_scores = {}
        score_errors = {}
        combined_results = chain(inprogress_results.items(), results.items())
        for rev_id, model_results in combined_results:
            if rev_id not in rev_scores:
                rev_scores[rev_id] = {}
            for model_name, score_result in model_results.items():
                try:
                    rev_scores[rev_id][model_name] = \
                        score_result.get(timeout=self.timeout)
                except celery.exceptions.TimeoutError:
                    timeout_error = errors.TimeoutError(
                        "Timed out after {0} seconds.".format(self.timeout))
                    score_errors[rev_id] = timeout_error
                    self.application.backend.mark_as_failure(
                        score_result.id, timeout_error)
                except Exception as error:
                    score_errors[rev_id] = error

        return rev_scores, score_errors

    def _lookup_inprogress_results(self, request, response):
        context = self[request.context_name]

        inprogress_results = {}
        for rev_id in request.rev_ids:
            injection_cache = request.injection_caches.get(rev_id)

            for model_name in request.model_names:
                if rev_id in response.scores and \
                   model_name in response.scores[rev_id]:
                    continue

                task_id = context.format_id_string(
                    model_name, rev_id, injection_cache=injection_cache)
                score_result = \
                    self._lookup_score_in_map.AsyncResult(task_id)
                if score_result.state in (REQUESTED, SENT,
                                          celery.states.STARTED,
                                          celery.states.SUCCESS):
                    logger.info("Found in-progress result for {0} -- {1}"
                                .format(task_id, score_result.state))
                    if rev_id in inprogress_results:
                        inprogress_results[rev_id][model_name] = score_result
                    else:
                        inprogress_results[rev_id] = {model_name: score_result}

        return inprogress_results

    def _register_model_set_revs_to_process(self, request, model_set_revs):
        context = self[request.context_name]

        for model_set, rev_ids in model_set_revs.items():
            for rev_id in rev_ids:
                for model_name in model_set:
                    injection_cache = request.injection_caches.get(rev_id)
                    task_id = context.format_id_string(
                        model_name, rev_id, injection_cache=injection_cache)
                    self.application.backend.store_result(
                        task_id, {}, REQUESTED)

    def _score(self, *args, **kwargs):
        self._check_queue_full()
        return super()._score(*args, **kwargs)

    def _check_queue_full(self):
        # Check redis to see if the queue of waiting tasks is too big.
        # This is a hack to implement backpressure because celery doesn't
        # support it natively.
        # This will result in a race condition, but it should have OK
        # properties.
        if self.redis is not None and self.queue_maxsize is not None:
            queue_size = self.redis.llen(DEFAULT_CELERY_QUEUE)
            if queue_size > self.queue_maxsize:
                message = "Queue size is too full {0}".format(queue_size)
                logger.warning(message)
                raise errors.ScoreProcessorOverloaded(message)

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
    r"(:(?P<password>[^@]+)@)?" +
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
