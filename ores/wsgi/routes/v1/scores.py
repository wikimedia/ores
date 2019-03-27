import traceback

from flask import request
from revscoring.errors import ModelInfoLookupError

from .... import errors
from ... import preprocessors, responses
from ...util import build_score_request, jsonify
from . import util


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
            scoring_system.metrics_collector.response_made(
                responses.SERVER_OVERLOADED, score_request)
            return responses.server_overloaded()
        except errors.MissingContext as e:
            scoring_system.metrics_collector.response_made(
                responses.NOT_FOUND, score_request)
            return responses.not_found("No scorers available for {0}"
                                       .format(e))
        except errors.MissingModels as e:
            scoring_system.metrics_collector.response_made(
                responses.NOT_FOUND, score_request)
            context_name, model_names = e.args
            return responses.not_found(
                "Models {0} not available for {1}"
                .format(tuple(model_names), context_name))
        except ModelInfoLookupError as e:
            return responses.model_info_lookup_error(e)
        except errors.TimeoutError:
            scoring_system.metrics_collector.response_made(
                responses.TIMEOUT, score_request)
            return responses.timeout_error()
        except errors.TooManyRequestsError:
            scoring_system.metrics_collector.response_made(
                responses.TOO_MANY_REQUESTS, score_request)
            return responses.too_many_requests_error()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

    # /scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/scores/<context>/", methods=["GET"])
    @bp.route("/v1/scores/<context>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_model_revisions(context):
        try:
            score_request = build_score_request(
                scoring_system, request, context)
        except Exception as e:
            return responses.bad_request(str(e))
        return process_score_request(score_request, context)

    # /scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/scores/<context>/<model>/", methods=["GET"])
    @bp.route("/v1/scores/<context>/<model>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revisions(context, model):
        try:
            score_request = build_score_request(
                scoring_system, request, context, model_name=model)
        except Exception as e:
            return responses.bad_request(str(e))

        return process_score_request(score_request, context, model)

    # /scores/enwiki/reverted/4567890
    @bp.route("/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @bp.route("/v1/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revision(context, model, rev_id):
        try:
            score_request = build_score_request(
                scoring_system, request, context, rev_id=rev_id,
                model_name=model)
        except Exception as e:
            return responses.bad_request(str(e))

        return process_score_request(score_request, context, model)

    return bp
