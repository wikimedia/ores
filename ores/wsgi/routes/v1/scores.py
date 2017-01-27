import traceback

from flask import request
from flask.ext.jsonpify import jsonify

from ... import preprocessors, responses
from .... import errors
from ...util import ParamError, nocache, read_bar_split_param


def configure(config, bp, scoring_system):

    # /scores/
    @bp.route("/scores/", methods=["GET"])
    @bp.route("/v1/scores/", methods=["GET"])
    @nocache
    @preprocessors.minifiable
    def scores():
        contexts = [context for context in scoring_system]

        contexts.sort()

        return jsonify({'contexts': contexts})

    # /scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/scores/<context>/", methods=["GET"])
    @bp.route("/v1/scores/<context>/", methods=["GET"])
    @nocache
    @preprocessors.minifiable
    def score_model_revisions(context):

        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        # If no model is specified, return information on available models
        if "models" not in request.args:
            # Return the models that we have
            model_info_doc = scoring_system.format_model_info(
                context, include_model_info="all")
            return jsonify({"models": model_info_doc})

        # Read the params
        try:
            models = set(read_bar_split_param(request, "models", type=str))
        except ParamError as e:
            return responses.bad_request(str(e))

        # Check if all the models are available
        missing_models = models - scoring_system[context].keys()
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
        try:
            score_doc = scoring_system.score(
                context, models, rev_ids, precache=precache)
            return jsonify(convert_score_doc(score_doc, model_flip=True))
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

    # /scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/scores/<context>/<model>/", methods=["GET"])
    @bp.route("/v1/scores/<context>/<model>/", methods=["GET"])
    @nocache
    @preprocessors.minifiable
    def score_revisions(context, model):

        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in scoring_system[context]:
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
            return jsonify(scoring_system.format_model_info(
                context, [model], include_model_info="all")[model])

        precache = "precache" in request.args
        try:
            score_doc = scoring_system.score(context, [model], rev_ids,
                                             precache=precache)
            return jsonify(convert_score_doc(score_doc)[model])
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

    # /scores/enwiki/reverted/4567890
    @bp.route("/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @bp.route("/v1/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @nocache
    @preprocessors.minifiable
    def score_revision(context, model, rev_id):

        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in scoring_system[context]:
            return responses.not_found("Model '{0}' not available for {1}."
                                       .format(model, context))

        precache = "precache" in request.args

        try:
            score_doc = scoring_system.score(context, [model], [rev_id],
                                             precache=precache)
            return jsonify(convert_score_doc(score_doc)[model])
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

    return bp


def convert_score_doc(score_doc, model_flip=False):
    v1_score_doc = {}
    if not model_flip:
        for model_name in score_doc['models']:
            v1_score_doc[model_name] = {}
            for rev_id, rev_score_error in score_doc['scores'].items():
                if 'error' in rev_score_error:
                    error_doc = rev_score_error
                    v1_score_doc[model_name][rev_id] = error_doc
                else:
                    rev_score = rev_score_error[model_name]['score']
                    v1_score_doc[model_name][rev_id] = rev_score
    else:
        for rev_id, rev_score_error in score_doc['scores'].items():
            v1_score_doc[rev_id] = {}
            if 'error' in rev_score_error:
                error_doc = rev_score_error
                for model_name in score_doc['models']:
                    v1_score_doc[rev_id][model_name] = error_doc
            else:
                for model_name in score_doc['models']:
                    v1_score_doc[rev_id][model_name] = \
                        rev_score_error[model_name]['score']

    return v1_score_doc
