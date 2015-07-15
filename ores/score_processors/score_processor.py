import logging
import time

import yamlconf

from ..score_caches import Empty

logger = logging.getLogger("ores.score_processors.score_processor")


class ScoreResult():
    def get(self, *args, **kwargs):
        raise NotImplementedError()

class ScoreProcessor(dict):

    def __init__(self, scoring_contexts, score_cache=None):
        super().__init__()
        self.update(scoring_contexts)
        self.score_cache = score_cache or Empty()

    def score(self, context, model, rev_ids, caches=None):
        # Remove dupes and prepares for set differences
        rev_ids = set(rev_ids)

        # Lookup cached scores
        scores = self._lookup_cached_scores(context, model, rev_ids)
        missing_rev_ids = rev_ids - scores.keys()

        # Generate scores for the rest
        scores.update(self._score(context, model, missing_rev_ids,
                                  caches=caches))

        return scores

    def _lookup_cached_scores(self, context, model, rev_ids):
        scores = {}

        scorer_model = self[context][model]

        # Lookup scores that are in the cache
        version = scorer_model.version
        for rev_id in rev_ids:
            try:
                score = self.score_cache.lookup(context, model, rev_id,
                                                version=version)

                logger.debug("Found cached score for {0}:{1}"
                             .format(model, rev_id))

                scores[rev_id] = score
            except KeyError:
                pass

        return scores

    def _score(self, context, model, rev_ids, caches=None):
        scores = {}

        # Batch extract root datasources for features of the missing ids
        scoring_context = self[context]
        root_ds_caches = scoring_context.extract_roots(model, rev_ids,
                                                       caches=caches)

        # Process scores for each revision using the cached data
        results = {}
        for rev_id in rev_ids:
            error, cache = root_ds_caches[rev_id]

            if error is None:
                results[rev_id] = self.process(context, model, rev_id, cache)
            else:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(error)),
                        'message': str(error)
                    }
                }

        for rev_id in results:
            try:
                scores[rev_id] = results[rev_id].get()
            except Exception as error:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(error)),
                        'message': str(error)
                    }
                }

        return scores

    def process(self, context, model, rev_id, cache):
        raise NotImplementedError()

    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):
        logger.info("Loading ScoreProcessor '{0}' from config.".format(name))
        section = config[section_key][name]
        if 'module' in section:
            return yamlconf.import_module(section['module'])
        elif 'class' in section:
            Class = yamlconf.import_module(section['class'])
            return Class.from_config(config, name)


class SimpleScoreProcessor(ScoreProcessor):

    def _process(self, context, model, rev_id, cache):
        scoring_context = self[context]
        return scoring_context.score(model, cache)

    def process(self, context, model, rev_id, cache):
        try:
            score = self._process(context, model, rev_id, cache)
            return SimpleScoreResult(score=score)
        except Exception as e:
            return SimpleScoreResult(error=e)

class SimpleScoreResult(ScoreResult):

    def __init__(self, *, score=None, error=None):
        self.score = score
        self.error = error

    def get(self):
        if self.error is not None:
            raise self.error
        else:
            return self.score
