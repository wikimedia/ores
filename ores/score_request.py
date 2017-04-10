import json


class ScoreRequest:
    def __init__(self, context_name, rev_ids, model_names, precache=False,
                 include_features=False, injection_caches=None,
                 model_info=None):
        """
        Construct a ScoreRequest from parameters.

        :Parameters:
            context_name : str
                The name of the content for the query -- usually a wikidb name
            rev_ids : `iterable` ( `int` )
                A set of revision IDs to score
            model_names : `iterable` ( `str` )
                A set of model_names to use in scoring
            precache : bool
                If true, mark the request as a "precache" request
            include_features : bool
                If true, include feature values in the response
            injection_caches : dict
                A mapping of injection_cache to `rev_id` to use for injecting
                cached data when extracting features/scoring.
            model_info : `list` ( `str` )
                A list of model information fields to include in the response
        """
        self.context_name = context_name
        self.rev_ids = set(rev_ids)
        self.model_names = set(model_names)
        self.precache = precache
        self.include_features = include_features
        self.injection_caches = injection_caches or {}
        self.model_info = model_info

    def __str__(self):
        return self.format()

    def format(self, rev_id=None, model_name=None):
        """
        Fomat a request or a sub-part of a request based on a rev_id and/or
        model_name.  This is useful for logging.
        """
        rev_ids = rev_id if rev_id is not None else set(self.rev_ids)
        model_names = model_name if model_name is not None else set(self.model_names)
        common = [self.context_name, rev_ids, model_names]

        optional = []
        if self.precache:
            optional.append("precache")
        if self.include_features:
            optional.append("features")
        if self.injection_caches:
            optional.append("injection_caches={0}".format(self.injection_caches))
        if self.model_info:
            optional.append("model_info=" + json.dumps(self.model_info))

        return "{0}({1})".format(":".join(repr(v) for v in common),
                                 ", ".join(optional))

    def __repr__(self):
        return "{0}({1})".format(
            self.__class__.__name__,
            ", ".join(repr(v) for v in [
                self.context_name,
                self.rev_ids,
                self.model_names,
                "precache={0!r}".format(self.precache),
                "include_features={0!r}".format(self.include_features),
                "injection_caches={0!r}".format(self.injection_caches),
                "model_info={0!r}".format(self.model_info)]))
