from collections import defaultdict

from flask import request
from flask.ext.jsonpify import jsonify

from .. import responses
from ..util import ParamError, read_bar_split_param


def configure(config, bp, score_processor):

    # /scores/
    @bp.route("/scores/", methods=["GET"])
    def scores():
        contexts = [context for context in score_processor]

        contexts.sort()

        return jsonify({'contexts': contexts})

    # /scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/scores/<context>/", methods=["GET"])
    def score_model_revisions(context):

        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        # If no model is specified, return information on available models
        if "models" not in request.args:
            # Return the models that we have
            models = {name: model.info()
                      for name, model in score_processor[context].items()}
            return jsonify({"models": models})

        # Read the params
        try:
            models = set(read_bar_split_param(request, "models", type=str))
        except ParamError as e:
            return responses.bad_request(str(e))

        # Check if all the models are available
        missing_models = models - score_processor[context].keys()
        if len(missing_models) > 0:
            return responses.bad_request("Models '{0}' not available for {1}."
                                         .format(list(missing_models), context))

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        if len(rev_ids) == 0:
            return responses.bad_request("No revids provided.")

        precache = "precache" in request.args

        # Generate scores for each model and merge them together
        scores = defaultdict(dict)
        for model in models:
            model_scores = score_processor.score(context, model, rev_ids,
                                                 precache=precache)
            for rev_id in model_scores:
                scores[rev_id][model] = model_scores[rev_id]

        return jsonify(scores)

    # /scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/scores/<context>/<model>/", methods=["GET"])
    def score_revisions(context, model):

        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in score_processor[context]:
            return responses.bad_request("Model '{0}' not available for {1}."
                                         .format(model, context))

        # Try to read the rev_ids
        if 'revids' in request.args:
            try:
                rev_ids = set(read_bar_split_param(request, "revids", type=int))
            except ParamError as e:
                return responses.bad_request(str(e))

            if len(rev_ids) == 0:
                return responses.bad_request("No revids provided.")
        else:
            return jsonify(score_processor[context][model].info())

        precache = "precache" in request.args
        scores = score_processor.score(context, model, rev_ids,
                                       precache=precache)
        return jsonify(scores)

    # /scores/enwiki/reverted/4567890
    @bp.route("/scores/<context>/<model>/<int:rev_id>/", methods=["GET"])
    def score_revision(context, model, rev_id):

        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        precache = "precache" in request.args

        # If the model exists, score revisions with it and return the result
        if model not in score_processor[context]:
            return responses.not_found("Model '{0}' not available for {1}."
                                       .format(model, context))
        else:
            scores = score_processor.score(context, model, [rev_id],
                                           precache=precache)
            return jsonify(scores)

    return bp
