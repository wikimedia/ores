import logging
from collections import defaultdict

from revscoring import dependencies
from revscoring.datasources import Datasource
from revscoring.extractors import Extractor
from revscoring.scorer_models import ScorerModel

from ..score_caches import Empty, ScoreCache
from ..score_processors import ScoreProcessor, Timeout

logger = logging.getLogger("ores.scorer.scorer")


class Scorer:

    def __init__(self, wiki, scorer_models, extractor, score_processor=None,
                 score_cache=None):
        """
        :Parameters:
            wiki : str
                The wiki that this scorer is being used for
            scorer_models : dict
                A mapping between names and
                :class:`~revscoring.scorer_models.scorer_model.ScorerModel`
                instances
            extractor : :class:`~revscoring.extractors.extractor.Extractor`
                An extractor to use for gathering feature values
            score_processor : A
                :class:`~ores.score_processors.score_processor.ScoreProcessor`
                to use doing the CPU intensive work.
            score_cache : :class:`~ores.score_caches.score_cache.ScoreCache`
                A cache to use for storing scores and looking up scores
        """
        self._check_compatibility(scorer_models, extractor)
        self.wiki = str(wiki)
        self.scorer_models = scorer_models
        self.extractor = extractor
        self.score_processor = score_processor or Timeout()
        self.score_cache = score_cache or Empty()

    def extract_roots(self, rev_ids, model, caches=None):
        """
        Extracts a mapping of root datasources capabile of generating the
        features needed for a particular model.

        :Parameters:
            rev_ids : int | `iterable`
                Revision IDs to extract for
            model : str
                The name of a
                :class:`~revscoring.scorer_models.scorer_model.ScorerModel` to
                extract the roots for
        """
        features = self.scorer_models[model].features
        root_ds = [d for d in dependencies.dig(features)
                   if isinstance(d, Datasource)]
        rev_root_vals = self.extractor.extract(rev_ids, root_ds, caches=caches)
        for e, root_vals in rev_root_vals:
            if e is None:
                yield None, {rd: rv for rd, rv in zip(root_ds, root_vals)}
            else:
                yield e, None

    def solve(self, model, cache=None):
        """
        Solves a model's features for a revision.  Does not attempt to gather
        new data.
        """
        features = self.scorer_models[model].features
        return self.extractor.solve(features, cache=cache)

    def score(self, rev_ids, model, caches=None):
        logger.debug("Generating {0} scores for {1}".format(model, rev_ids))
        caches = caches or defaultdict(dict)

        scores = {}
        scorer_model = self.scorer_models[model]

        logger.debug("Starting request with ")

        # Lookup in-progress processors
        results = {}
        for rev_id in rev_ids:
            id = (self.wiki, model, rev_id, scorer_model.version)
            try:
                result = self.score_processor.in_progress(id)
                results[rev_id] = result
            except KeyError:
                pass

        missing_ids = set(rev_ids) - results.keys()

        # Lookup scores that are in the cache
        version = scorer_model.version
        for rev_id in missing_ids:
            try:
                score = self.score_cache.lookup(self.wiki, model, rev_id,
                                                version=version)
                scores[rev_id] = score

                logger.debug("Found cached score for {0}:{1}"
                             .format(model, rev_id))
            except KeyError:
                pass

        missing_ids = list(missing_ids - scores.keys())

        # Extract roots into caches
        error_roots = self.extract_roots(missing_ids, model, caches=caches)
        for rev_id, (e, roots) in zip(missing_ids, error_roots):
            if e is None:
                caches[rev_id].update(roots)
            else:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(e)),
                        'message': str(e)
                    }
                }
                # TODO: log error?

        # Filters out the errors we just logged.
        missing_ids = missing_ids - scores.keys()

        # Farm this out to a distributed process
        for rev_id in missing_ids:
            id = (self.wiki, model, rev_id, scorer_model.version)
            results[rev_id] = self.score_processor.process(scorer_model,
                                                           self.extractor,
                                                           cache=caches[rev_id],
                                                           id=id)

        # TODO: Get results
        for rev_id in missing_ids:
            try:
                id = (self.wiki, model, rev_id, scorer_model.version)
                result = self.score_processor.process(scorer_model,
                                                      self.extractor,
                                                      cache=caches[rev_id],
                                                      id=id)

                results[rev_id] = result
            except RuntimeError as e:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(e)),
                        'message': str(e)
                    }
                }

        for rev_id, result in results.items():
            try:
                score = result.get()
                self.score_cache.store(self.wiki, model, rev_id, score,
                                       version=scorer_model.version)
                scores[rev_id] = score
            except RuntimeError as e:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(e)),
                        'message': str(e)
                    }
                }
            finally:
                if hasattr(result, 'traceback'):
                    logger.error(result.traceback)

        return scores

    def _check_compatibility(self, scorer_models, extractor):
        for scorer_model in scorer_models.values():
            if scorer_model.language is not None and \
               extractor.language != scorer_model.language:
                raise ValueError(("Model language {0} does not match " +
                                  "extractor language {1}")
                                 .format(scorer_model.language.name,
                                         extractor.language.name))

    @classmethod
    def from_config(cls, config, name, section_key="scorers"):
        """
        Expects:

            scorers:
                enwiki:
                    scorer_models:
                        damaging: enwiki_damaging_2014
                        good-faith: enwiki_good-faith_2014
                    extractor: enwiki
                ptwiki:
                    scorer_models:
                        damaging: ptwiki_damaging_2014
                        good-faith: ptwiki_good-faith_2014
                    extractor: ptwiki

            extractors:
                enwiki_api: ...
                ptwiki_api: ...

            scorer_models:
                enwiki_damaging_2014: ...
                enwiki_good-faith_2014: ...
        """
        logger.info("Loading Scorer '{0}' from config.".format(name))
        section = config[section_key][name]

        wiki = name

        scorer_models = {}
        for name, key in section['scorer_models'].items():
            scorer_model = ScorerModel.from_config(config, key)
            scorer_models[name] = scorer_model

        extractor = Extractor.from_config(config, section['extractor'])

        if 'score_cache' in section:
            score_cache = ScoreCache.from_config(config, section['score_cache'])
        else:
            score_cache = None

        if 'score_processor' in section:
            score_processor = \
                ScoreProcessor.from_config(config, section['score_processor'])
        else:
            score_processor = None

        return cls(wiki, scorer_models=scorer_models, extractor=extractor,
                   score_processor=score_processor, score_cache=score_cache)
