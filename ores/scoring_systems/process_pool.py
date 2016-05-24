import logging
from concurrent import futures as cfutures

from .scoring_system import ScoringSystem
from ..errors import TimeoutError

logger = logging.getLogger(__name__)


class ProcessPool(ScoringSystem):

    def __init__(self, *args, workers=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.workers = int(workers) if workers is not None else None

    def _process_missing_scores(self, context_name, missing_model_set_revs,
                                root_caches, injection_caches,
                                include_features, inprogress_results=None):
        rev_scores = {}
        errors = {}

        futures = {}
        with cfutures.ProcessPoolExecutor(max_workers=self.workers) as executor:
            for missing_models, rev_ids in missing_model_set_revs.items():
                for rev_id in rev_ids:
                    root_cache = root_caches[rev_id]
                    future = executor.submit(
                        self._process_score_map,
                        context_name, missing_models, rev_id, root_cache,
                        injection_caches.get(rev_id), include_features)
                    futures[rev_id] = future

            for rev_id, future in futures.items():
                try:
                    rev_scores[rev_id] = future.result(timeout=self.timeout)
                except cfutures.TimeoutError:
                    errors[rev_id] = TimeoutError(
                        "Timed out after {0} seconds.".format(self.timeout))
                except Exception as error:
                    errors[rev_id] = error

        return rev_scores, errors

    @classmethod
    def from_config(cls, config, name, section_key="scoring_systems"):
        logger.info("Loading ProcessPool '{0}' from config.".format(name))
        section = config[section_key][name]

        kwargs = cls._kwargs_from_config(
            config, name, section_key=section_key)
        workers = section.get('workers')

        return cls(workers=workers, **kwargs)
