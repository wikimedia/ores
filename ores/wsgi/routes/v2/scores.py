import traceback

from flask import request
from revscoring.errors import ModelInfoLookupError

from .... import errors
from ... import preprocessors, responses
from ...util import build_score_request
from . import util


def configure(config, bp, scoring_system):

    # /v2/scores/
    @bp.route("/v2/scores/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def scores_v2():
        try:
            score_request = build_score_request(scoring_system, request)
        except Exception as e:
            return responses.bad_request(str(e))

        return util.build_v2_context_model_map(score_request, scoring_system)

    def process_score_request(score_request):
        try:
            score_response = scoring_system.score(score_request)
            return util.format_v2_score_response(score_request, score_response)
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

    # /v2/scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/v2/scores/<context>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_model_revisions_v2(context):
        try:
            score_request = build_score_request(
                scoring_system, request, context)
        except Exception as e:
            return responses.bad_request(str(e))

        return process_score_request(score_request)

    # /v2/scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/v2/scores/<context>/<model>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revisions_v2(context, model):
        try:
            score_request = build_score_request(
                scoring_system, request, context, model_name=model)
        except Exception as e:
            return responses.bad_request(str(e))

        return process_score_request(score_request)

    # /v2/scores/enwiki/reverted/4567890
    @bp.route("/v2/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revision_v2(context, model, rev_id):
        try:
            score_request = build_score_request(
                scoring_system, request, context, rev_id=rev_id,
                model_name=model)
        except Exception as e:
            return responses.bad_request(str(e))

        return process_score_request(score_request)

    return bp
