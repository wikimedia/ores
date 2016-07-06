import logging
import time
from hashlib import sha1

from revscoring import dependencies
from revscoring.datasources import Datasource
from revscoring.extractors import Extractor
from revscoring.features import trim
from revscoring.scorer_models import ScorerModel

logger = logging.getLogger(__name__)


class ScoringContext(dict):

    def __init__(self, name, model_map, extractor):
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
        self.update(model_map)
        self.extractor = extractor

    def format_model_info(self, model_names, fields=None):
        fields = fields or ['version']
        model_info = {}
        for model_name in model_names:
            formatted_info = self._get_model_info_for(model_name)
            filtered_info = {field: value
                             for field, value in formatted_info.items()
                             if fields == "all" or field in fields}

            model_info[model_name] = filtered_info

        return model_info

    def format_id_string(self, model_name, rev_id, injection_cache=None):
        version = self.model_version(model_name)
        score_id = ":".join(
            str(v) for v in [self.name, model_name, version, rev_id])
        if injection_cache is None:
            return score_id
        else:
            sorted_tuple = tuple(sorted(injection_cache.items()))
            cache_hash = sha1(bytes(str(sorted_tuple), 'utf8')).hexdigest()
            return score_id + ":" + cache_hash

    def _get_model_info_for(self, model_name):
        return self[model_name].format_info(format='json')

    def model_version(self, model_name):
        return self[model_name].version

    def model_features(self, model_name):
        return self[model_name].features

    def process_model_scores(self, model_names, root_cache, include_features):
        model_scores = {}

        for model_name in model_names:
            model_scores[model_name] = {}

            # Mostly CPU
            model_scores[model_name]['score'] = \
                self.process_score(model_name, dependency_cache=root_cache)

            # Essentially free
            if include_features:
                base_feature_map = self.solve_base_feature_map(
                    model_name, dependency_cache=root_cache)
                model_scores[model_name]['features'] = base_feature_map

        return model_scores

    def solve_features(self, model_name, dependency_cache=None):
        """
        """
        features = self[model_name].features
        return list(self.extractor.solve(features, cache=dependency_cache))

    def solve_base_feature_map(self, model_name, dependency_cache=None):
        """
        """
        features = list(trim(self[model_name].features))
        feature_values = self.extractor.solve(features, cache=dependency_cache)
        return {str(f): v
                for f, v in zip(features, feature_values)}

    def process_score(self, model_name, dependency_cache=None):
        """
        """
        version = self[model_name].version

        start = time.time()
        feature_values = list(self.solve_features(
            model_name, dependency_cache))
        logger.debug("Extracted features for {0}:{1}:{2} in {3} secs"
                     .format(self.name, model_name, version,
                             time.time() - start))

        start = time.time()
        score = self[model_name].score(feature_values)
        logger.debug("Scored features for {0}:{1}:{2} in {3} secs"
                     .format(self.name, model_name, version,
                             time.time() - start))

        return score

    def _generate_root_datasources(self, model_names):
        for model_name in model_names:
            for dependency in dependencies.dig(self.model_features(model_name)):
                if isinstance(dependency, Datasource):
                    yield dependency

    def extract_root_dependency_caches(
            self, model_names, rev_ids, injection_caches=None):
        """
        Extracts a mapping of root datasources capable of generating the
        features needed for a particular set of models.

        :Parameters:
            model_names : `list` ( `str` )
                The names of a :class:`~revscoring.ScorerModel` to
                extract the roots dependencies for
        """
        # Make a copy of dependency_caches
        root_caches = {}
        for rev_id in rev_ids:
            injection_cache = injection_caches.get(rev_id) \
                              if injection_caches is not None else {}
            root_caches[rev_id] = {key: value
                                   for key, value in injection_cache.items()}

        # Find our root datasources
        root_datasources = \
            list(set(self._generate_root_datasources(model_names)))

        # Extract the root datasource and update the root_caches in-place
        start = time.time()
        error_root_vals = self.extractor.extract(
            rev_ids, root_datasources, caches=root_caches)

        # Check each extraction for errors
        errors = {}
        for rev_id, (error, root_vals) in zip(rev_ids, error_root_vals):
            if error is not None:
                errors[rev_id] = error
                del root_caches[rev_id]
        logger.debug("Extracted root datasources for {0}:{1}:{2} in {3} secs"
                     .format(self.name, set(model_names), rev_ids,
                             round(time.time() - start, 3)))

        # Note that root_caches should have been modified in place
        return root_caches, errors

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

        model_map = {}
        for model_name, key in section['scorer_models'].items():
            scorer_model = ScorerModel.from_config(config, key)
            model_map[model_name] = scorer_model

        extractor = Extractor.from_config(config, section['extractor'])

        return cls(name, model_map=model_map, extractor=extractor)


class ClientScoringContext(ScoringContext):

    def __init__(self, name, model_map, *args, **kwargs):
        # Load an empty model map
        bare_model_map = {model_name: NotImplemented
                          for model_name, model in model_map.items()}
        super().__init__(name, bare_model_map, *args, **kwargs)

        # Create an info map for use when formatting information
        self.info_map = {model_name: model.format_info(format='json')
                         for model_name, model in model_map.items()}
        self.features_map = {model_name: model.features
                             for model_name, model in model_map.items()}

    def _get_model_info_for(self, model_name):
        return self.info_map[model_name]

    def model_version(self, model_name):
        return self.info_map[model_name].get("version")

    def model_features(self, model_name):
        return self.features_map[model_name]
