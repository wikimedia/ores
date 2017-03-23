import json


class ScoreRequest:
    def __init__(self, context_name, rev_ids, model_names, precache=False,
                 include_features=False, injection_caches=None,
                 model_info=None):
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
        rev_ids = rev_id if rev_id is not None else self.rev_ids
        model_names = model_name if model_name is not None else self.model_names
        common = [self.context_name, rev_ids, model_names]

        optional = []
        if self.precache:
            optional.append("precache")
        if self.include_features:
            optional.append("features")
        if self.injection_caches:
            if rev_id is None:
                optional.append("injection_caches=" +
                                json.dumps(self.injection_caches))
            elif self.injection_caches.get(rev_id) is not None:
                optional.append("injection_cache=" +
                                json.dumps(self.injection_caches.get(rev_id)))
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
