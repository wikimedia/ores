import logging
import re
from itertools import chain
from urllib.parse import urlparse

import celery
import celery.exceptions
import celery.states
import mwapi.errors
import revscoring.errors
from ores.score_request import ScoreRequest

from .. import errors
from ..task_tracker import NullTaskTracker, RedisTaskTracker
from .scoring_system import ScoringSystem

logger = logging.getLogger(__name__)

_applications = []

DEFAULT_CELERY_QUEUE = "celery"
SENT = "SENT"
REQUESTED = "REQUESTED"


class CeleryQueue(ScoringSystem):

    def __init__(self, *args, application, queue_maxsize=None,
                 task_tracker=None, **kwargs):
        super().__init__(*args, **kwargs)
        global _applications
        self.application = application
        self.queue_maxsize = int(queue_maxsize) if queue_maxsize is not None \
                             else None

        self.redis = redis_from_url(self.application.conf.BROKER_URL)

        self.task_tracker = task_tracker or NullTaskTracker()

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
            if not isinstance(request, ScoreRequest):
                request = ScoreRequest.from_json(request)

            if not isinstance(model_names, frozenset):
                model_names = frozenset(model_names)

            logger.info("Generating a score map for {0}"
                        .format(request.format(rev_id, model_names)))

            score_map = ScoringSystem._process_score_map(
                self, request, rev_id, model_names,
                root_cache=root_cache)
            logger.info("Completed generating score map for {0}"
                        .format(request.format(rev_id, model_names)))
            return score_map

        self._process_score_map = _process_score_map

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
                            model_name, rev_id, request,
                            injection_cache=injection_cache)
                        self.application.backend.mark_as_failure(
                            task_id, RuntimeError("Never started"))
                    continue
                root_cache = {str(k): v for k, v in root_caches[rev_id].items()}
                result = self._process_score_map.delay(
                    request.to_json(), list(missing_models), rev_id, root_cache)
                self._lock_process(missing_models, rev_id, request,
                                   injection_cache, result.id)

                for model_name in missing_models:
                    if rev_id in results:
                        results[rev_id][model_name] = result
                    else:
                        results[rev_id] = {model_name: result}

        # Read results
        rev_scores = {}
        score_errors = {}
        combined_results = chain(inprogress_results.items(), results.items())
        for rev_id, model_results in combined_results:
            injection_cache = request.injection_caches.get(rev_id)
            if rev_id not in rev_scores:
                rev_scores[rev_id] = {}
            for model_name, score_result in model_results.items():
                try:
                    task_result = score_result.get(timeout=self.timeout)
                except celery.exceptions.TimeoutError:
                    timeout_error = errors.TimeoutError(
                        "Timed out after {0} seconds.".format(self.timeout))
                    score_errors[rev_id] = timeout_error
                    self.application.backend.mark_as_failure(
                        score_result.id, timeout_error)
                except Exception as error:
                    score_errors[rev_id] = error
                else:
                    if model_name in task_result:
                        rev_scores[rev_id][model_name] = task_result[model_name]
                    else:
                        raise RuntimeError('Model is not in the task but '
                                           'the task locked the model')

                    key = context.format_id_string(
                        model_name, rev_id, request,
                        injection_cache=injection_cache)
                    self.task_tracker.release(key)

        return rev_scores, score_errors

    def _lock_process(self, models, rev_id, request, injection_cache,
                      task_id):
        context = self[request.context_name]
        for model in models:
            key = context.format_id_string(
                    model, rev_id, request,
                    injection_cache=injection_cache)
            self.task_tracker.lock(key, task_id)

    def _lookup_inprogress_results(self, request, response):
        context = self[request.context_name]

        inprogress_results = {}
        for rev_id in request.rev_ids:
            injection_cache = request.injection_caches.get(rev_id)

            for model_name in request.model_names:
                if rev_id in response.scores and \
                   model_name in response.scores[rev_id]:
                    continue

                key = context.format_id_string(
                    model_name, rev_id, request,
                    injection_cache=injection_cache)
                task_id = self.task_tracker.get_in_progress_task(key)
                if task_id:
                    score_result = \
                        self._process_score_map.AsyncResult(task_id)
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
                        model_name, rev_id, request,
                        injection_cache=injection_cache)
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
    def from_config(cls, config, name, section_key="scoring_systems"):
        from ores import ores
        from ..scoring_context import ServerScoringContext, ClientScoringContext

        logger.info("Loading CeleryQueue '{0}' from config.".format(name))
        section = config[section_key][name]

        if hasattr(ores, "_is_wsgi_client") and ores._is_wsgi_client:
            ScoringContextClass = ClientScoringContext
        else:
            ScoringContextClass = ServerScoringContext

        kwargs = cls._kwargs_from_config(
            config, name, section_key=section_key, ScoringContextClass=ScoringContextClass)
        queue_maxsize = section.get('queue_maxsize')

        if 'task_tracker' in section:
            task_tracker = RedisTaskTracker.from_config(
                config, section['task_tracker'])
        else:
            task_tracker = None

        application = celery.Celery(__name__)
        application.conf.update(**{k: v for k, v in section.items()
                                   if k not in ('class', 'context_map',
                                                'score_cache',
                                                'metrics_collector', 'timeout',
                                                'queue_maxsize')})

        return cls(application=application,
                   queue_maxsize=queue_maxsize,
                   task_tracker=task_tracker, **kwargs)


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
