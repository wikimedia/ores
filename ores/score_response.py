from collections import defaultdict


class ScoreResponse:

    def __init__(self, context, request, model_info=None, scores=None,
                 errors=None, features=None):
        """
        Initialize features.

        Args:
            self: (todo): write your description
            context: (str): write your description
            request: (dict): write your description
            model_info: (str): write your description
            scores: (todo): write your description
            errors: (str): write your description
            features: (todo): write your description
        """
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
        """
        Add a score to the model.

        Args:
            self: (todo): write your description
            rev_id: (str): write your description
            model_name: (str): write your description
            score: (str): write your description
        """
        self.scores[rev_id][model_name] = score

    def add_error(self, rev_id, model_name, error):
        """
        Add a single error to the error.

        Args:
            self: (todo): write your description
            rev_id: (str): write your description
            model_name: (str): write your description
            error: (todo): write your description
        """
        self.errors[rev_id][model_name] = error

    def add_features(self, rev_id, model_name, features):
        """
        Add features to the model.

        Args:
            self: (todo): write your description
            rev_id: (str): write your description
            model_name: (str): write your description
            features: (todo): write your description
        """
        self.features[rev_id][model_name] = features

    def add_model_info(self, model_name, info_doc):
        """
        Add a model info to the model

        Args:
            self: (todo): write your description
            model_name: (str): write your description
            info_doc: (todo): write your description
        """
        self.model_info[model_name] = info_doc
