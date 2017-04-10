from collections import defaultdict


class ScoreResponse:

    def __init__(self, context, request, model_info=None, scores=None,
                 errors=None, features=None):
        self.context = context
        self.request = request
        self.scores = defaultdict(dict)
        self.errors = defaultdict(dict)
        self.features = defaultdict(dict)
        self.model_info = {}

        scores = scores or []
        errors = errors or []
        features = features or []
        model_info = model_info or []

        for rev_id, model_name, score in scores:
            self.add_score(rev_id, model_name, score)
        for rev_id, model_name, error in scores:
            self.add_error(rev_id, model_name, error)
        for rev_id, model_name, feature_vals in features:
            self.add_features(rev_id, model_name, feature_vals)
        for model_name, info_doc in model_info:
            self.add_model_info(model_name, info_doc)

    def add_score(self, rev_id, model_name, score):
        self.scores[rev_id][model_name] = score

    def add_error(self, rev_id, model_name, error):
        self.errors[rev_id][model_name] = error

    def add_features(self, rev_id, model_name, features):
        self.features[rev_id][model_name] = features

    def add_model_info(self, model_name, info_doc):
        self.model_info[model_name] = info_doc
