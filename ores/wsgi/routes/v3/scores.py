import traceback

from flask import request

from . import util
from ... import preprocessors, responses
from .... import errors
from ...util import build_score_request


def configure(config, bp, scoring_system):

    # /v3/scores/
    @bp.route("/v3/scores/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def scores_v3():
        score_request = build_score_request(scoring_system, request)
        return util.build_v3_context_model_map(score_request, scoring_system)

    def process_score_request(score_request):
        score_request.model_info = score_request.model_info or ['version']
        try:
            score_response = scoring_system.score(score_request)
            return util.format_v3_score_response(score_response)
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except errors.MissingContext as e:
            return responses.not_found("No scorers available for {0}"
                                       .format(e[0]))
        except errors.MissingModels as e:
            context_name, model_names = e.args
            return responses.not_found(
                "Models {0} not available for {1}"
                .format(tuple(model_names), context_name))
        except Exception:
            return responses.unknown_error(traceback.format_exc())

    # /v3/scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/v3/scores/<context>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_model_revisions_v3(context):
        score_request = build_score_request(scoring_system, request, context)
        return process_score_request(score_request)

    # /v3/scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/v3/scores/<context>/<int:revid>/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revisions_v3(context, revid):
        score_request = build_score_request(
            scoring_system, request, context, rev_id=revid)
        return process_score_request(score_request)

    # /v3/scores/enwiki/reverted/4567890
    @bp.route("/v3/scores/<context>/<int:rev_id>/<model>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revision_v3(context, model, rev_id):
        score_request = build_score_request(
            scoring_system, request, context, rev_id=rev_id, model_name=model)
        return process_score_request(score_request)

    return bp
