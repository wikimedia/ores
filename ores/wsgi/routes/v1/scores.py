import traceback

from flask import request
from flask.ext.jsonpify import jsonify

from . import util
from ... import preprocessors, responses
from .... import errors
from ...util import build_score_request


def configure(config, bp, scoring_system):

    # /scores/
    @bp.route("/scores/", methods=["GET"])
    @bp.route("/v1/scores/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def scores():
        contexts = [context for context in scoring_system]

        contexts.sort()

        return jsonify({'contexts': contexts})

    def process_score_request(score_request, context=None, model=None):
        try:
            if len(score_request.rev_ids) == 0:
                return util.format_some_model_info(
                    scoring_system, score_request, model)
            else:
                score_response = scoring_system.score(score_request)
                return util.format_v1_score_response(score_response, model)
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except errors.MissingContext as e:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))
        except errors.MissingModels as e:
            context_name, model_names = e.args
            return responses.not_found(
                "Models {0} not available for {1}"
                .format(tuple(model_names), context_name))
        except Exception:
            return responses.unknown_error(traceback.format_exc())

    # /scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/scores/<context>/", methods=["GET"])
    @bp.route("/v1/scores/<context>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_model_revisions(context):
        score_request = build_score_request(scoring_system, request, context)
        return process_score_request(score_request, context)

    # /scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/scores/<context>/<model>/", methods=["GET"])
    @bp.route("/v1/scores/<context>/<model>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revisions(context, model):
        score_request = build_score_request(
            scoring_system, request, context, model_name=model)
        return process_score_request(score_request, context, model)

    # /scores/enwiki/reverted/4567890
    @bp.route("/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @bp.route("/v1/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revision(context, model, rev_id):
        score_request = build_score_request(
            scoring_system, request, context, rev_id=rev_id, model_name=model)
        return process_score_request(score_request, context, model)

    return bp
