from collections import defaultdict

from flask import request
from flask.ext.jsonpify import jsonify

from ... import responses
from .... import errors
from ...util import ParamError, format_output, read_bar_split_param


def configure(config, bp, score_processor):

    # /v2/scores/
    @bp.route("/v2/scores/", methods=["GET"])
    def scores_v2():
        contexts = [context for context in score_processor]

        contexts.sort()

        return jsonify({'contexts': contexts})

    # /v2/scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/v2/scores/<context>/", methods=["GET"])
    def score_model_revisions_v2(context):

        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        # If no model is specified, return information on available models
        if "models" not in request.args:
            # Return the models that we have
            models = {name: model.format_info(format="json")
                      for name, model in score_processor[context].items()}
            return jsonify({"models": models})

        # Read the params
        try:
            models = set(read_bar_split_param(request, "models", type=str))
        except ParamError as e:
            return responses.bad_request(str(e))

        # Get model info
        try:
            model_info_req = set(read_bar_split_param(request, "model_info", type=str))
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

        # Get model info for each model and merge them togethe
        scores = defaultdict(dict)
        model_info = {}
        try:
            for model in models:
                model_object = score_processor[context][model]
                model_info[model] = {'version': model_object.version}
                if model_info_req:
                    try:
                        for req in model_info_req:
                            model_info[model][req] = model_object.format_info(format="json")[req]
                    except KeyError:
                        return responses.bad_request(
                            "Model '{0}' has not attribute {1}.".format(
                                model, req))
                model_scores = score_processor.score(
                    context, model, rev_ids, precache=precache)
                scores[model] = model_scores
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        return format_output(context, scores, model_info)

    # /v2/scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/v2/scores/<context>/<model>/", methods=["GET"])
    def score_revisions_v2(context, model):

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
            return jsonify(score_processor[context][model].format_info(format="json"))

        # Get model info
        try:
            model_info_req = set(read_bar_split_param(request, "model_info", type=str))
        except ParamError as e:
            return responses.bad_request(str(e))

        precache = "precache" in request.args
        try:
            model_object = score_processor[context][model]
            model_info = {model: {'version': model_object.version}}
            if model_info_req:
                for req in model_info_req:
                    try:
                        model_info[model][req] = model_object.format_info(format="json")[req]
                    except KeyError:
                        return responses.bad_request(
                            "Model '{0}' has not attribute {1}.".format(
                                model, req))
            scores = {model: score_processor.score(context, model, rev_ids,
                                                   precache=precache)}
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        return format_output(context, scores, model_info)

    # /v2/scores/enwiki/reverted/4567890
    @bp.route("/v2/scores/<context>/<model>/<int:rev_id>/", methods=["GET"])
    def score_revision_v2(context, model, rev_id):

        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        precache = "precache" in request.args
        model_object = score_processor[context][model]
        model_info = {model: {'version': model_object.version}}
        scores = {}
        # If the model exists, score revisions with it and return the result
        if model not in score_processor[context]:
            return responses.not_found("Model '{0}' not available for {1}."
                                       .format(model, context))

        # Get model info
        try:
            model_info_req = set(read_bar_split_param(
                request, "model_info", type=str))
        except ParamError as e:
            return responses.bad_request(str(e))
        if model_info_req:
            for req in model_info_req:
                try:
                    model_info[model][req] = model_object.format_info(format="json")[req]
                except KeyError:
                    return responses.bad_request(
                        "Model '{0}' has no attribute {1}.".format(
                            model, req))
        try:
            scores = {model: score_processor.score(
                context, model, [rev_id], precache=precache)}
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()

        return format_output(context, scores, model_info)

    return bp
