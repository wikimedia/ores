import logging
import time
import traceback

from .. import errors
from ..metrics_collectors import Null
from ..score_caches import Empty
from ..util import jsonify_error

logger = logging.getLogger(__name__)


class ScoreProcessor(dict):

    def __init__(self, scoring_contexts, score_cache=None,
                       metrics_collector=None):
        super().__init__()
        self.update(scoring_contexts)
        self.score_cache = score_cache or Empty()
        self.metrics_collector = metrics_collector or Null()

    def score(self, context, model, rev_ids, caches=None,
              include_features=False, precache=False):
        version = self[context].version(model)
        start = time.time()
        if caches is not None:
            logger.debug("Scoring {0}:{1}:{2} with caches {3}"
                         .format(context, model, rev_ids, version, caches))

        try:
            scores = self._score(context, model, rev_ids, caches=caches,
                                 include_features=include_features)
        except errors.ScoreProcessorOverloaded:
            self.metrics_collector.score_processor_overloaded(
                context, model, version)
            raise

        duration = time.time() - start
        if not precache:
            self.metrics_collector.scores_request(context, model, version,
                                                  len(rev_ids), duration)
        else:
            self.metrics_collector.precache_request(context, model, version,
                                                    duration)

        return scores

    def _get_root_ds(self, context, model, rev_ids, caches=None):
        """
        Pure IO.  Batch extract root datasources for a set of features that the
        model needs.
        """
        if len(rev_ids) == 0:
            return {}
        rev_ids = set(rev_ids)
        scoring_context = self[context]
        version = scoring_context.version(model)

        start = time.time()
        roots = scoring_context.extract_roots(model, rev_ids, caches=caches)
        duration = time.time() - start
        logger.debug("Extracted root datasources for "
                     "{0}:{1}:{2}:{3} in {4} secs"
                     .format(context, model, version, rev_ids, duration))

        self.metrics_collector.datasources_extracted(context, model,
                                                     version, len(rev_ids),
                                                     duration)

        for error, cache in roots.values():
            if error is not None:
                logger.error("Errored while getting root datasource "
                             "for {0}:{1}:{2}:{3}"
                             .format(context, model, version, rev_ids))
                self.metrics_collector.score_errored(context, model, version)

        return roots

    def _process(self, context, model, cache, include_features=False):
        """
        Pure CPU.  Extract features from datasources in the cache and apply the
        model to arrive at a score.
        """
        scoring_context = self[context]
        version = scoring_context[model].version

        try:
            start = time.time()
            score, feature_vals = scoring_context.score(
                    model, cache, include_features=include_features)
            duration = time.time() - start
            logger.debug("Scoring {0}:{1}:{2} took {3} secs"
                         .format(context, model, version, duration))
            self.metrics_collector.score_processed(context, model, version,
                                                   duration)
        except:
            self.metrics_collector.score_errored(context, model, version)
            logger.error("Errored while scoring {0}:{1}:{2}"
                         .format(context, model, version))
            raise

        return score, feature_vals

    def _score_revision(self, context, model, rev_id, cache=None,
                        include_features=False):
        """
        Both IO and CPU.  Generates a single score or an error.
        """
        error, score_cache = self._get_root_ds(context, model, [rev_id],
                                               caches={rev_id: cache})[rev_id]

        if error is not None:
            raise error

        return self._process(context, model, score_cache,
                             include_features=include_features)

    def _store(self, context, model, rev_id, score, cache):
        version = self[context].version(model)

        self.score_cache.store(context, model, rev_id, score, cache=cache,
                               version=version)

    def _lookup_cached_scores(self, context, model, rev_ids, caches):
        version = self[context][model].version

        scores = {}
        for rev_id in rev_ids:
            cache = (caches or {}).get(rev_id, {})
            try:
                score = self.score_cache.lookup(context, model, rev_id,
                                                version=version, cache=cache)

                logger.debug("Found cached score for {0}:{1}:{2}{3}"
                             .format(context, model, rev_id,
                                     ":w/cache" if len(cache) > 0 else ""))

                self.metrics_collector.score_cache_hit(context, model, version)
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
        else:
            raise RuntimeError("No module or class to load.")


class SimpleScoreProcessor(ScoreProcessor):

    def _score(self, context, model, rev_ids, caches=None,
               include_features=False):
        rev_ids = set(rev_ids)

        # Look in the cache
        if not include_features:
            scores = self._lookup_cached_scores(context, model, rev_ids,
                                                caches)
            missing_ids = rev_ids - scores.keys()
        else:
            scores = {}
            missing_ids = rev_ids

        feature_maps = {}

        # Get the root datasources for the rest of the batch (IO)
        root_ds_caches = self._get_root_ds(context, model, missing_ids,
                                           caches=caches)

        # Extract features and generate scores (CPU)
        for rev_id, (error, cache) in root_ds_caches.items():
            if error is not None:
                scores[rev_id] = {'error': jsonify_error(error)}
            else:
                try:
                    score, feature_vals = \
                        self._process(context, model, cache,
                                      include_features=include_features)
                    scores[rev_id] = score
                    feature_maps[rev_id] = feature_vals
                    cache = (caches or {}).get(rev_id, {})
                    self._store(context, model, rev_id, score, cache)
                except Exception as error:
                    logger.debug(traceback.format_exc())
                    scores[rev_id] = {'error': jsonify_error(error)}

        return scores, feature_maps
