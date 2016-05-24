import logging
import time

from .. import errors
from ..metrics_collectors import Null
from ..score_caches import Empty
from ..util import jsonify_error, timeout

logger = logging.getLogger(__name__)


class ScoringSystem(dict):

    def __init__(self, context_map, score_cache=None,
                       metrics_collector=None, timeout=None):
        super().__init__()
        self.update(context_map)
        self.score_cache = score_cache or Empty()
        self.metrics_collector = metrics_collector or Null()
        self.timeout = timeout

    def score(self, context_name, model_names, rev_ids, injection_caches=None,
              precache=False, include_features=False, include_model_info=None):
        model_names = set(model_names)
        start = time.time()
        logger.debug("Scoring {0}:{1}:{2}{3}"
                     .format(context_name, model_names, rev_ids,
                             " w/cache = {0}".format(injection_caches)
                             if injection_caches else ""))

        try:
            scores_doc = self._score(
                context_name, model_names, rev_ids,
                injection_caches=injection_caches, include_features=False,
                include_model_info=None)
        except errors.ScoreProcessorOverloaded:
            self.metrics_collector.score_processor_overloaded(
                context_name, model_names)
            raise

        duration = time.time() - start
        if not precache:
            self.metrics_collector.scores_request(
                context_name, model_names, len(rev_ids), duration)
        else:
            self.metrics_collector.precache_request(
                context_name, model_names, duration)

        return scores_doc

    def _score(self, context_name, model_names, rev_ids, injection_caches=None,
               include_features=False, include_model_info=None):
        rev_ids = set(rev_ids)

        # 0. Get model information
        model_info = self._format_model_info(
            context_name, model_names, include_model_info)

        # 1. Lookup cached and inprogress scores (Fast IO)
        if not include_features:
            # Can't use cached score if we want feature values since those
            # will need to be regenerated
            rev_scores = self._lookup_cached_scores(
                context_name, model_names, rev_ids,
                injection_caches=injection_caches)
            inprogress_results = self._lookup_inprogress_results(
                context_name, model_names, rev_ids,
                injection_caches=injection_caches, rev_scores=rev_scores)
        else:
            rev_scores = {}
            inprogress_results = {}

        # 2. Get missing rev_model sets
        missing_model_set_revs = self._filter_missing_model_set_revs(
            context_name, model_names, rev_ids, rev_scores=rev_scores,
            inprogress_results=inprogress_results)

        # 2.5 Register inprogress work
        self._register_model_set_revs_to_process(
            context_name, missing_model_set_revs, injection_caches)

        # 3. Extract base datasources for missing models (Slow IO)
        root_caches, extraction_errors = self._extract_root_caches(
            context_name, missing_model_set_revs, rev_ids,
            injection_caches=injection_caches)

        # 3.5. Record extraction errors
        for rev_id, error in extraction_errors:
            rev_scores[rev_id] = jsonify_error(error)

        # 4. Generate scores (Heavy CPU)
        missing_scores, scoring_errors = self._process_missing_scores(
            context_name, missing_model_set_revs, root_caches,
            injection_caches, include_features,
            inprogress_results=inprogress_results)
        for rev_id, model_scores in missing_scores.items():
            if rev_id not in rev_scores:
                rev_scores[rev_id] = model_scores
            else:
                for model_name, score in model_scores:
                    rev_scores[rev_id][model_name] = score

        # 4.5 Record scoring errors
        for rev_id, error in scoring_errors.items():
            rev_scores[rev_id] = jsonify_error(error)

        return {
            'models': model_info,
            'scores': rev_scores
        }

    def _extract_root_caches(self, context_name, missing_model_set_revs,
                             rev_ids, injection_caches=None):
        context = self[context_name]

        root_caches = {}
        errors = {}
        for model_set, rev_ids in missing_model_set_revs.items():

            ms_root_caches, ms_errors = context.extract_root_dependency_caches(
                model_set, rev_ids, injection_caches=injection_caches)
            root_caches.update(ms_root_caches)
            errors.update(ms_errors)

        return root_caches, errors

    def _process_score_map(self, context_name, model_names, rev_id, root_cache,
                           injection_cache, include_features):
        context = self[context_name]

        start = time.time()
        # Runs a timeout function so that we don't get stuck here
        score_map = timeout(
            context.process_model_scores, model_names, root_cache,
            include_features=include_features, seconds=self.timeout)
        duration = time.time() - start

        logger.debug("Score generated for {0}:{1} in {2} seconds"
                     .format(context_name, model_names, round(duration, 3)))
        self.metrics_collector.score_processed(
            context_name, model_names, duration)

        self._cache_scores(rev_id, score_map, context_name,
                           injection_cache=injection_cache)

        return score_map

    def _process_missing_scores(self, context_name, missing_model_set_revs,
                                root_caches, injection_caches,
                                include_features):
        raise NotImplementedError()

    def _format_model_info(self, context_name, model_names, include_model_info):
        context = self[context_name]
        if not include_model_info:
            fields = ['version']
        else:
            fields = include_model_info

        return context.format_model_info(model_names, fields=fields)

    def _filter_missing_model_set_revs(self, context_name, model_names, rev_ids,
                                       rev_scores=None,
                                       inprogress_results=None):
        rev_scores = rev_scores or {}
        inprogress_results = inprogress_results or {}
        missing_model_set_rev_pairs = self._filter_missing_model_pairs(
            model_names, rev_ids, rev_scores, inprogress_results)
        missing_model_set_revs = {}
        for model_set, rev_id in missing_model_set_rev_pairs:
            if len(model_set) == 0:
                continue
            if model_set in missing_model_set_revs:
                missing_model_set_revs[model_set].append(rev_id)
            else:
                missing_model_set_revs[model_set] = [rev_id]

        return missing_model_set_revs

    def _filter_missing_model_pairs(self, model_names, rev_ids, rev_scores,
                                    inprogress_results):
        for rev_id in rev_ids:
            missing_models = model_names - (
                set(rev_scores.get(rev_id, {}).keys()) |
                set(inprogress_results.get(rev_id, {}).keys()))

            yield frozenset(missing_models), rev_id

    def _register_model_set_revs_to_process(self, context_name,
                                            missing_model_set_revs,
                                            injection_caches):
        return None

    def _cache_scores(self, rev_id, score_map, context_name,
                      injection_cache=None):
        for model_name, score_doc in score_map.items():
            self._cache_score(score_doc, context_name, model_name, rev_id,
                              injection_cache=injection_cache)

    def _cache_score(self, score_doc, context_name, model_name, rev_id,
                     injection_cache):
        version = self[context_name].model_version(model_name)

        self.score_cache.store(
            score_doc, context_name, model_name, rev_id, version=version,
            injection_cache=injection_cache)

    def _lookup_inprogress_results(self, context_name, model_names, rev_ids,
                                   injection_caches=None, rev_scores=None):
        return {}

    def _lookup_cached_scores(self, context_name, model_names, rev_ids,
                              injection_caches=None):

        rev_scores = {}
        for rev_id in rev_ids:
            for model_name in model_names:
                try:
                    rev_score = self._lookup_cached_score(
                        context_name, model_name, rev_id,
                        injection_cache=injection_caches.get(rev_id))
                    if rev_id in rev_scores:
                        rev_scores[rev_id][model_name] = rev_score
                    else:
                        rev_scores[rev_id] = {model_name: rev_score}
                except KeyError:
                    pass

        return rev_scores

    def _lookup_cached_score(self, context_name, model_name, rev_id,
                             injection_cache=None):
        version = self[context_name][model_name].version
        try:
            score = self.score_cache.lookup(
                context_name, model_name, rev_id,
                version=version, injection_cache=injection_cache)

            logger.debug("Found cached score for {0}:{1}:{2}{3}"
                         .format(context_name, model_name, rev_id,
                                 ":w/cache" if injection_cache else ""))

            self.metrics_collector.score_cache_hit(
                context_name, model_name, version)
            return score
        except KeyError:
            self.metrics_collector.score_cache_miss(
                context_name, model_name, version)
            raise

    @classmethod
    def _build_context_map(cls, config, name, section_key="scoring_systems"):
        from ..scoring_contexts import ScoringContext

        section = config[section_key][name]

        return {name: ScoringContext.from_config(config, name)
                for name in section['scoring_contexts']}

    @classmethod
    def _kwargs_from_config(cls, config, name, section_key="scoring_systems"):
        from ..metrics_collectors import MetricsCollector
        from ..score_caches import ScoreCache

        section = config[section_key][name]

        context_map = cls._build_context_map(
            config, name, section_key=section_key)

        if 'score_cache' in section:
            score_cache = ScoreCache.from_config(config, section['score_cache'])
        else:
            score_cache = None

        if 'metrics_collector' in section:
            metrics_collector = MetricsCollector.from_config(
                config, section['metrics_collector'])
        else:
            metrics_collector = None

        timeout = section.get('timeout')

        return {'context_map': context_map, 'score_cache': score_cache,
                'metrics_collector': metrics_collector, 'timeout': timeout}

    @classmethod
    def from_config(cls, config, name, section_key="scoring_systems"):
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
