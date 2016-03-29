import logging
import time

from revscoring import dependencies
from revscoring.datasources import Datasource
from revscoring.extractors import Extractor
from revscoring.features import trim
from revscoring.scorer_models import ScorerModel

logger = logging.getLogger(__name__)


class ScoringContext(dict):

    def __init__(self, name, scorer_models, extractor):
        """
        :Parameters:
            name : str
               The  that this scorer is being used for
            scorer_models : dict
               A mapping between names and
               :class:`revscoring.ScorerModel`
               instances
            extractor : :class:`revscoring.Extractor`
               An extractor to use for gathering feature values
        """
        super().__init__()
        self.name = str(name)
        self.update(scorer_models)
        self.extractor = extractor

    def solve_features(self, model, cache=None):
        """
        Solves a model's features for a revision.  Does not attempt to gather
        new data.
        """
        features = self[model].features
        return self.extractor.solve(features, cache=cache)

    def solve_base_features(self, model, cache=None):
        """
        Solves a model's basic features for a revision.  Does not attempt to
        gather new data.
        """
        features = list(trim(self[model].features))
        feature_values = self.extractor.solve(features, cache=cache)
        return {"feature." + f.name: v
                for f, v in zip(features, feature_values)}

    def version(self, model):
        return self[model].version

    def score(self, model, cache=None, include_features=False):
        """
        I am the score function
        """
        version = self[model].version

        # TODO: record time spend computing features
        start = time.time()
        feature_values = list(self.solve_features(model, cache))
        logger.debug("Extracted features for {0}:{1}:{2} in {3} secs"
                     .format(self.name, model, version, time.time() - start))

        # TODO: record time spent generating a score
        start = time.time()
        score = self[model].score(feature_values)
        logger.debug("Scored features for {0}:{1}:{2} in {3} secs"
                     .format(self.name, model, version, time.time() - start))

        if include_features:
            start = time.time()
            feature_vals = self.solve_base_features(model, cache)
            logger.debug("Re-extracted base features for " +
                         "{0}:{1}:{2} in {3} secs"
                         .format(self.name, model, version, time.time() - start))
        else:
            feature_vals = None

        return score, feature_vals

    def extract_roots(self, model, rev_ids, caches=None):
        """
        Extracts a mapping of root datasources capabile of generating the
        features needed for a particular model.

        :Parameters:
            rev_ids : int | `iterable`
                Revision IDs to extract for
            model : str
                The name of a :class:`~revscoring.ScorerModel` to
                extract the roots for
        """
        features = self[model].features
        root_ds = [d for d in dependencies.dig(features)
                   if isinstance(d, Datasource)]
        error_root_vals = self.extractor.extract(rev_ids, root_ds,
                                                 caches=caches)
        root_ds_caches = {}
        for rev_id, (error, root_vals) in zip(rev_ids, error_root_vals):
            if error is None:
                root_ds_map = {rd: rv for rd, rv in zip(root_ds, root_vals)}
                if caches is not None:
                    root_ds_map.update(caches.get(rev_id, {}))
                root_ds_caches[rev_id] = (None, root_ds_map)
            else:
                root_ds_caches[rev_id] = (error, None)

        return root_ds_caches

    @classmethod
    def from_config(cls, config, name, section_key="scoring_contexts"):
        """
        Expects:

            scoring_contexts:
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
        logger.info("Loading ScoringContext '{0}' from config.".format(name))
        section = config[section_key][name]

        scorer_models = {}
        for model_name, key in section['scorer_models'].items():
            scorer_model = ScorerModel.from_config(config, key)
            scorer_models[model_name] = scorer_model

        extractor = Extractor.from_config(config, section['extractor'])

        return cls(name, scorer_models=scorer_models, extractor=extractor)
