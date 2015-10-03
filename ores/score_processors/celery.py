import logging

import celery
import revscoring.errors
from celery.signals import before_task_publish

import mwapi.errors

from ..score_caches import ScoreCache
from ..metrics_collectors import MetricsCollector
from ..util import jsonify_error
from .timeout import Timeout, TimeoutError

logger = logging.getLogger(__name__)

APPLICATIONS = []


@before_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):

    for application in APPLICATIONS:
        task = application.tasks.get(sender)
        backend = task.backend if task else application.backend

        logger.debug("Setting state to 'SENT' for {0}".format(body['id']))
        backend.store_result(body['id'], result=None, status="SENT")


class Celery(Timeout):

    def __init__(self, *args, application, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application

        expected_errors = (revscoring.errors.RevisionNotFound,
                           revscoring.errors.DependencyError,
                           mwapi.errors.RequestError,
                           mwapi.errors.TimeoutError,
                           TimeoutError)

        @self.application.task(throws=expected_errors)
        def _process_task(context, model, cache):
            return Timeout._process(self, context, model, cache)

        @self.application.task(throws=expected_errors)
        def _score_revision_task(context, model, rev_id, cache=None):
            return Timeout._score_revision(self, context, model, rev_id, cache=cache)

        APPLICATIONS.append(application)

        self._process_task = _process_task

        self._score_revision_task = _score_revision_task

    def _score_in_celery(self, context, model, rev_ids, caches):
        scores = {}
        results = {}

        if len(rev_ids) == 0:
            return scores
        if len(rev_ids) == 1:  # Special case -- do everything in celery
            rev_id = rev_ids.pop()
            id_string = self._generate_id(context, model, rev_id)
            cache = (caches or {}).get(rev_id, {})
            result = self._score_revision_task.apply_async(
                args=(context, model, rev_id), kwargs={'cache': cache},
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
                    id_string = self._generate_id(context, model, rev_id)
                    result = self._process_task.apply_async(
                        args=(context, model, cache),
                        task_id=id_string
                    )
                    results[rev_id] = result

        # Process async results
        for rev_id, result in results.items():
            try:
                score = result.get(self.timeout)
                scores[rev_id] = score
                self._store(context, model, rev_id, score)
            except Exception as error:
                scores[rev_id] = {'error': jsonify_error(error)}

        return scores

    def _generate_id(self, context, model, rev_id):
        scorer_model = self[context][model]
        version = scorer_model.version

        return ":".join(str(v) for v in [context, model, rev_id, version])

    def _score(self, context, model, rev_ids, caches=None):
        rev_ids = set(rev_ids)

        # Lookup scoring results that are currently in progress
        results = self._lookup_inprogress_results(context, model, rev_ids)
        missing_ids = rev_ids - results.keys()

        # Lookup scoring results that are in the cache
        scores = self._lookup_cached_scores(context, model, missing_ids)
        missing_ids = missing_ids - scores.keys()

        # Generate scores for missing rev_ids
        scores.update(self._score_in_celery(context, model, missing_ids,
                                            caches=caches))

        # Gather results
        for rev_id in results:
            try:
                scores[rev_id] = results[rev_id].get(self.timeout)
            except Exception as error:
                scores[rev_id] = {'error': jsonify_error(error)}

        # Return scores
        return scores

    def _lookup_inprogress_results(self, context, model, rev_ids):

        results = {}
        for rev_id in rev_ids:
            id_string = self._generate_id(context, model, rev_id)
            try:
                results[rev_id] = self._get_result(id_string)
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
        application = celery.Celery('ores.score_processors.celery')
        application.conf.update(**{k: v for k, v in section.items()
                                   if k not in ('class', 'timeout')})

        return cls(scoring_contexts, application=application, timeout=timeout,
                   score_cache=score_cache,
                   metrics_collector=metrics_collector)
