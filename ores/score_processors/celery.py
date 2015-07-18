import logging

import celery
from celery.signals import after_task_publish

from ..score_caches import ScoreCache
from .score_processor import ScoreResult
from .timeout import timeout as timeout_func
from .timeout import Timeout

logger = logging.getLogger("ores.score_processors.celery")


class CeleryTimeoutResult(ScoreResult):

    def __init__(self, async_result, timeout):
        self.async_result = async_result
        self.timeout = timeout

    def get(self):
        return self.async_result.get(timeout=self.timeout)


class Celery(Timeout):

    def __init__(self, *args, application, **kwargs):
        super().__init__(*args, **kwargs)
        self.application = application

        # This sets up a state updater that will set a state to "SENT" when
        # a task is actually started.  This allows us to differentate between
        # async-results that are in-process and those that do not exist.
        @after_task_publish.connect
        def update_sent_state(sender=None, body=None, **kwargs):
            # the task may not exist if sent using `send_task` which
            # sends tasks by name, so fall back to the default result backend
            # if that is the case.
            task = application.tasks.get(sender)
            backend = task.backend if task else application.backend

            backend.store_result(body['id'], None, "SENT")

        @self.application.task
        def _process(context, model, cache):
            scoring_context = self[context]
            score = scoring_context.score(model, cache)
            return score

        self._process = _process

    def _generate_id(self, context, model, rev_id):
        scorer_model = self[context][model]
        version = scorer_model.version

        return ":".join(str(v) for v in [context, model, rev_id, version])

    def process(self, context, model, rev_id, cache):
        id_string = self._generate_id(context, model, rev_id)

        result = self._process.apply_async(args=(context, model, cache),
                                           task_id=id_string)
        return CeleryTimeoutResult(result, self.timeout)

    def score(self, context, model, rev_ids):
        rev_ids = set(rev_ids)

        # Lookup scoring results that are currently in progress
        results = self._lookup_inprogress_results(context, model, rev_ids)
        missing_rev_ids = rev_ids - results.keys()

        # Lookup scoring results that are in the cache
        scores = self._lookup_cached_scores(context, model, missing_rev_ids)
        missing_rev_ids = missing_rev_ids - scores.keys()

        # Generate scores for missing rev_ids
        scores.update(self._score(context, model, missing_rev_ids))

        # Gather results
        for rev_id in results:
            try:
                scores[rev_id] = results[rev_id].get()
            except Exception as e:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(error)),
                        'message': str(error)
                    }
                }

        # Return scores
        return scores


    def _lookup_inprogress_results(self, context, model, rev_ids):
        scorer_model = self[context][model]
        version = scorer_model.version

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
        logger.debug("Checking if {0} is already being processed"
                     .format(repr(id_string)))
        result = self._process.AsyncResult(task_id=id_string)
        logging.info("Found task {0} with state {1}" \
                      .format(id_string, result.state))
        if result.state not in ("STARTED", "SUCCESS", "SENT"):
            raise KeyError(id_string)
        else:
            logger.debug("Found AsyncResult for {0}".format(repr(id_string)))
            return result

    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):

        if 'data_paths' in config['ores'] and \
           'nltk' in config['ores']['data_paths']:
            import nltk
            nltk.data.path.append(config['ores']['data_paths']['nltk'])

        from ..scoring_contexts import ScoringContext

        section = config[section_key][name]

        scoring_contexts = {name: ScoringContext.from_config(config, name)
                            for name in section['scoring_contexts']}

        if 'score_cache' in section:
            score_cache = ScoreCache.from_config(config, section['score_cache'])
        else:
            score_cache = None

        timeout = section.get('timeout')
        application = celery.Celery('ores.score_processors.celery')
        application.conf.update(**{k: v for k, v in section.items()
                                   if k not in ('class', 'timeout')})

        return cls(scoring_contexts, score_cache=score_cache,
                   application=application, timeout=timeout)
