import logging
import time

import revscoring.errors
import stopit

from .. import errors
from ..errors import MissingContext, MissingModels, TimeoutError
from ..metrics_collectors import Null
from ..score_caches import Empty
from ..score_response import ScoreResponse
from ..util import timeout

logger = logging.getLogger(__name__)


class ScoringSystem(dict):

    def __init__(self, context_map, score_cache=None,
                       metrics_collector=None, timeout=None):
        super().__init__()
        self.update(context_map)
        self.score_cache = score_cache or Empty()
        self.metrics_collector = metrics_collector or Null()
        self.timeout = timeout

    def check_context_models(self, request):

        if request.context_name not in self:
            raise MissingContext(request.context_name)

        missing_models = request.model_names - self[request.context_name].keys()
        if len(missing_models) > 0:
            raise MissingModels(request.context_name, missing_models)

    def score(self, request):
        self.check_context_models(request)
        start = time.time()
        logger.debug("Scoring {0}".format(request))

        try:
            response = self._score(request)
        except errors.ScoreProcessorOverloaded:
            self.metrics_collector.score_processor_overloaded(request)
            raise

        duration = time.time() - start
        if not request.precache:
            self.metrics_collector.scores_request(request, duration)
        else:
            self.metrics_collector.precache_request(request, duration)

        return response

    def _score(self, request):
        context = self[request.context_name]
        response = ScoreResponse(context, request)

        # 0. Get model info (if applicable)
        if request.model_info:
            self._build_model_info(request, response)

        # 1. Lookup cached and inprogress scores (Fast IO)
        if not request.include_features:
            # Can't use cached score if we want feature values since those
            # will need to be regenerated
            self._lookup_cached_scores(request, response)
            inprogress_results = self._lookup_inprogress_results(
                request, response)
        else:
            inprogress_results = {}

        # 2. Get missing rev_model sets
        missing_model_set_revs = self._filter_missing_model_set_revs(
            request, response, inprogress_results=inprogress_results)

        # 2.5 Register inprogress work
        self._register_model_set_revs_to_process(
            request, missing_model_set_revs)

        # 3. Extract base datasources for missing models (Slow IO)
        start = time.time()
        root_caches, extraction_errors = self._extract_root_caches(
            request, missing_model_set_revs)
        self.metrics_collector.datasources_extracted(
            request, sum(len(ids) for ids in missing_model_set_revs.values()),
            time.time() - start)

        # 3.5. Record extraction errors
        for rev_id, error in extraction_errors.items():
            for model in request.model_names:
                response.add_error(rev_id, model, error)
                self.metrics_collector.score_errored(request, model)

        # 4. Generate scores (Heavy CPU)
        missing_scores, scoring_errors = self._process_missing_scores(
            request, missing_model_set_revs, root_caches,
            inprogress_results=inprogress_results)
        for rev_id, score_map in missing_scores.items():
            for model_name, model_score in score_map.items():
                response.add_score(rev_id, model_name, model_score['score'])
                if request.include_features:
                    response.add_features(
                        rev_id, model_name, model_score['features'])

            # Store scores in cache
            self._cache_scores(request, rev_id, score_map)

        # 4.5 Record scoring errors
        for rev_id, error in scoring_errors.items():
            for model in request.model_names:
                response.add_error(rev_id, model, error)
                self.metrics_collector.score_errored(request, model)

        return response

    def _build_model_info(self, request, response):
        context = self[request.context_name]
        for model_name in request.model_names:
            response.add_model_info(
                model_name,
                context.format_model_info(model_name, request.model_info))

    def _extract_root_caches(self, request, missing_model_set_revs):
        context = self[request.context_name]

        root_caches = {}
        errors = {}
        for model_set, rev_ids in missing_model_set_revs.items():
            ms_root_caches, ms_errors = context.extract_root_dependency_caches(
                model_set, rev_ids, injection_caches=request.injection_caches)
            root_caches.update(ms_root_caches)
            errors.update(ms_errors)

        return root_caches, errors

    def _process_score_map(self, request, rev_id, model_names, root_cache):
        context = self[request.context_name]

        start = time.time()
        # Runs a timeout function so that we don't get stuck here
        try:
            score_map = timeout(
                context.process_model_scores, model_names, root_cache,
                include_features=request.include_features,
                seconds=self.timeout)
        except revscoring.errors.CaughtDependencyError as e:
            if isinstance(e.exception, stopit.TimeoutException):
                duration = time.time() - start
                self.metrics_collector.score_timed_out(request, duration)
                raise TimeoutError("Timed out after {0} seconds."
                                   .format(duration))
            else:
                raise
        except TimeoutError:
            duration = time.time() - start
            self.metrics_collector.score_timed_out(request, duration)
            raise

        duration = time.time() - start

        logger.debug("Score generated for {0}:{1} in {2} seconds"
                     .format(request.context_name, set(request.model_names),
                             round(duration, 3)))
        self.metrics_collector.score_processed(request, duration)

        return score_map

    def _process_missing_scores(self, request, missing_model_set_revs,
                                root_caches):
        raise NotImplementedError()

    def _filter_missing_model_set_revs(self, request, response,
                                       inprogress_results=None):
        missing_model_set_rev_pairs = self._filter_missing_model_pairs(
            request, response, inprogress_results)
        missing_model_set_revs = {}
        for model_set, rev_id in missing_model_set_rev_pairs:
            if len(model_set) == 0:
                continue
            if model_set in missing_model_set_revs:
                missing_model_set_revs[model_set].append(rev_id)
            else:
                missing_model_set_revs[model_set] = [rev_id]

        return missing_model_set_revs

    def _filter_missing_model_pairs(self, request, response,
                                    inprogress_results):
        for rev_id in request.rev_ids:
            missing_models = request.model_names - (
                set(response.scores.get(rev_id, {}).keys()) |
                set(inprogress_results.get(rev_id, {}).keys()))

            yield frozenset(missing_models), rev_id

    def _register_model_set_revs_to_process(self, request,
                                            missing_model_set_revs):
        return None

    def _cache_scores(self, request, rev_id, score_map):
        for model_name, score_doc in score_map.items():
            self._cache_score(request, rev_id, model_name, score_doc)

    def _cache_score(self, request, rev_id, model_name, score_doc):
        version = self[request.context_name].model_version(model_name)
        injection_cache = request.injection_caches.get(rev_id)
        self.score_cache.store(
            score_doc['score'], request.context_name, model_name,
            rev_id, version=version, injection_cache=injection_cache)

    def _lookup_inprogress_results(self, request, response):
        return {}

    def _lookup_cached_scores(self, request, response):

        for rev_id in request.rev_ids:
            for model_name in request.model_names:
                try:
                    rev_score = self._lookup_cached_score(
                        request, rev_id, model_name)
                    response.add_score(model_name, rev_id, rev_score)
                except KeyError:
                    pass

    def _lookup_cached_score(self, request, rev_id, model_name):
        version = self[request.context_name].model_version(model_name)
        injection_cache = request.injection_caches.get(rev_id)
        try:
            score = self.score_cache.lookup(
                request.context_name, model_name, rev_id,
                version=version, injection_cache=injection_cache)

            logger.debug("Found cached score for {0}"
                         .format(request.format(rev_id, model_name)))

            self.metrics_collector.score_cache_hit(request, model_name)
            return score
        except KeyError:
            self.metrics_collector.score_cache_miss(request, model_name)
            raise

    @classmethod
    def _build_context_map(cls, config, name, section_key="scoring_systems"):
        from ..scoring_context import ScoringContext

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
