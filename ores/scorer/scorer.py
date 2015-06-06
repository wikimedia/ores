from collections import defaultdict

from revscoring import dependencies
from revscoring.datasources import Datasource

from ..score_caches import Empty, ScoreCache


class Scorer:

    def __init__(self, wiki, scorer_models, extractor, score_cache=None):
        """
        :Parameters:
            wiki : str
                The wiki that this scorer is being used for
            scorer_models : dict
                A mapping between names and `ScorerModel` instances
            extractor : `revscoring.extractors.Extractor`
                An extractor to use for gathering feature values
            score_cache : `ores.score_caches.Cache`
                A cache to use for storing scores and looking up scores
        """
        self._check_compatibility(scorer_models, extractor)
        self.wiki = str(wiki)
        self.scorer_models = scorer_models
        self.extractor = extractor
        self.score_cache = score_cache or Empty()

    def extract_roots(self, rev_ids, model, caches=None):
        """
        Extracts a mapping of root datasources capabile of generating the
        features needed for a particular model.
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
        Solves a feature set for a revision.  Does not attempt to gather
        new data.
        """
        features = self.scorer_models[model].features
        return self.extractor.solve(features, cache=cache)

    def score(self, rev_ids, model, caches=None):
        caches = caches or defaultdict(dict)

        scores = {}
        scorer_model = self.scorer_models[model]

        # TODO: Lookup already-started celery tasks and get AsyncResults

        # Lookup scores that are in the cache
        version = scorer_model.version
        for rev_id in rev_ids:
            try:
                score = self.score_cache.lookup(self.wiki, model, rev_id, version=version)
                scores[rev_id] = score
            except KeyError:
                pass

        missing_ids = rev_ids - scores.keys()

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

        # TODO: Farm this out to celery
        for rev_id in missing_ids:
            try:
                feature_values = next(self.solve(model, cache=caches[rev_id]))
                score = scorer_model.score(feature_values)
                self.score_cache.store(self.wiki, model, rev_id, score,
                                       version=version)
                scores[rev_id] = score
            except Exception as e:
                scores[rev_id] = {
                    'error': {
                        'type': str(type(e)),
                        'message': str(e)
                    }
                }

        return scores

    def _check_compatibility(self, scorer_models, extractor):
        for scorer_model in scorer_models.values():
            if scorer_model.language is not None and \
               extractor.language != scorer_model.language:
                raise ValueError(("Model language {0} does not match " +
                                  "extractor language {1}") \
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
        section = config[section_key][name]

        wiki = name

        scorer_models = {}
        for name, key in section['scorer_models'].items():
            scorer_model = ScorerModel.from_config(config, key)
            scorer_models[name] = scorer_model

        extractor = Extractor.from_config(config, section['extractor'])

        if 'score_cache' in section:
            score_cache = Cache.from_config(config, section['score_cache'])

        return cls(wiki, scorer_models, extractor)
