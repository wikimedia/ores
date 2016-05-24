from .scoring_system import ScoringSystem


class SingleThread(ScoringSystem):

    def _process_missing_scores(self, context_name, missing_model_set_revs,
                                root_caches, injection_caches,
                                include_features, inprogress_results=None):
        rev_scores = {}
        errors = {}

        for missing_models, rev_ids in missing_model_set_revs.items():
            for rev_id in rev_ids:
                root_cache = root_caches[rev_id]
                try:
                    score_map = self._process_score_map(
                        context_name, missing_models, rev_id, root_cache,
                        injection_caches.get(rev_id), include_features)
                    rev_scores[rev_id] = score_map
                except Exception as error:
                    errors[rev_id] = error

        return rev_scores, errors

    @classmethod
    def from_config(cls, config, name, section_key="scoring_systems"):
        kwargs = cls._kwargs_from_config(
            config, name, section_key=section_key)
        return cls(**kwargs)
