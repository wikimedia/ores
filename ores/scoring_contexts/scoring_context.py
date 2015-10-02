import logging
import time

from revscoring import dependencies
from revscoring.datasources import Datasource
from revscoring.extractors import Extractor
from revscoring.scorer_models import ScorerModel

logger = logging.getLogger("ores.scorer.scorer")


class ScoringContext(dict):

    def __init__(self, name, scorer_models, extractor):
        """
        :Parameters:
            name : str
               The  that this scorer is being used for
            scorer_models : dict
               A mapping between names and
               :class:`~revscoring.scorer_models.scorer_model.ScorerModel`
               instances
            extractor : :class:`~revscoring.extractors.extractor.Extractor`
               An extractor to use for gathering feature values
        """
        super().__init__()
        self.name = str(name)
        self.update(scorer_models)
        self.extractor = extractor

    def solve(self, model, cache):
        """
        Solves a model's features for a revision.  Does not attempt to gather
        new data.
        """
        features = self[model].features
        return self.extractor.solve(features, cache=cache)

    def version(self, model):
        return self[model].version

    def score(self, model, cache):
        # TODO: record time spend computing features
        start = time.time()
        feature_values = list(self.solve(model, cache))
        logger.debug("Extracted features for {0}.{1} in {2} seconds"
                     .format(self.name, model, time.time() - start))

        # TODO: record time spent generating a score
        start = time.time()
        score = self[model].score(feature_values)
        logger.debug("Scored features for {0}.{1} in {2} seconds"
                     .format(self.name, model, time.time() - start))

        return score

    def extract_roots(self, model, rev_ids, caches=None):
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
        features = self[model].features
        root_ds = [d for d in dependencies.dig(features)
                   if isinstance(d, Datasource)]
        error_root_vals = self.extractor.extract(rev_ids, root_ds,
                                                 caches=caches)
        root_ds_caches = {}
        for rev_id, (error, root_vals) in zip(rev_ids, error_root_vals):
            if error is None:
                root_ds_caches[rev_id] = \
                        (None, {rd: rv for rd, rv in zip(root_ds, root_vals)})
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
        for name, key in section['scorer_models'].items():
            scorer_model = ScorerModel.from_config(config, key)
            scorer_models[name] = scorer_model

        extractor = Extractor.from_config(config, section['extractor'])

        return cls(name, scorer_models=scorer_models, extractor=extractor)
