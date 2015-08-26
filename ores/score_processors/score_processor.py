import logging
import time

from ..score_caches import Empty

logger = logging.getLogger("ores.score_processors.score_processor")


class ScoreProcessor(dict):

    def __init__(self, scoring_contexts, score_cache=None):
        super().__init__()
        self.update(scoring_contexts)
        self.score_cache = score_cache or Empty()

    def _get_root_ds(self, context, model, rev_ids, caches=None):
        """
        Pure IO.  Batch extract root datasources for a set of features that the
        model needs.
        """
        rev_ids = set(rev_ids)
        scoring_context = self[context]
        return scoring_context.extract_roots(model, rev_ids, caches=caches)

    def _process(self, context, model, cache):
        """
        Pure CPU.  Extract features from datasources in the cache and apply the
        model to arrive at a score.
        """
        scoring_context = self[context]
        score = scoring_context.score(model, cache)
        return score

    def _score(self, context, model, rev_id, cache=None):
        """
        Both IO and CPU.  Generates a single score or an error.
        """
        error, process_cache = self._get_root_ds(context, model, [rev_id],
                                                 caches={rev_id: cache})[rev_id]

        if error is not None:
            raise error

        return self._process(context, model, process_cache)

    def _store(self, context, model, rev_id, score):
        scorer_model = self[context][model]
        version = scorer_model.version

        self.score_cache.store(context, model, rev_id, score, version=version)


    def _lookup_cached_scores(self, context, model, rev_ids):
        scorer_model = self[context][model]
        version = scorer_model.version

        scores = {}
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

    @classmethod
    def from_config(cls, config, name, section_key="score_processors"):
        try:
            import yamlconf
        except ImportError:
            raise ImportError("Could not find yamlconf.  This packages is " +
                              "required when using yaml config files.")
        logger.info("Loading ScoreProcessor '{0}' from config.".format(name))
        section = config[section_key][name]
        if 'module' in section:
            return yamlconf.import_module(section['module'])
        elif 'class' in section:
            Class = yamlconf.import_module(section['class'])
            return Class.from_config(config, name)


class SimpleScoreProcessor(ScoreProcessor):

    def score(self, context, model, rev_ids, caches=None):
        rev_ids = set(rev_ids)

        # Look in the cache
        scores = self._lookup_cached_scores(context, model, rev_ids)
        missing_ids = rev_ids - scores.keys()

        # Get the root datasources for the rest of the batch (IO)
        root_ds_caches = self._get_root_ds(context, model, missing_ids,
                                           caches=caches)

        # Extract features and generate scores (CPU)
        for rev_id, (error, cache) in root_ds_caches.items():
            if error is not None:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(error)),
                        'message': str(error)
                    }
                }
            else:
                try:
                    score = self._process(context, model, cache)
                    scores[rev_id] = score
                    self._store(context, model, rev_id, score)
                except Exception as error:
                    scores[rev_id] = {
                        'error': {
                            'type': str(type(error)),
                            'message': str(error)
                        }
                    }

        return scores
