from flask import request

from . import util
from ... import preprocessors, responses
from ...util import build_score_request


def configure(config, bp, scoring_system):
    """
    Configure a bocities request.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
        scoring_system: (todo): write your description
    """

    # /v3/scores/
    @bp.route("/v3/scores/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def scores_v3():
        """
        Computes the score score for a score.

        Args:
        """
        try:
            score_request = build_score_request(scoring_system, request)
        except Exception as e:
            return responses.bad_request(str(e))

        return util.build_v3_context_model_map(score_request, scoring_system)

    # /v3/scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/v3/scores/<context>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_model_revisions_v3(context):
        """
        Compute the score.

        Args:
            context: (todo): write your description
        """
        try:
            score_request = build_score_request(
                scoring_system, request, context)
        except Exception as e:
            return responses.bad_request(str(e))

        return util.process_score_request(score_request, scoring_system)

    # /v3/scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/v3/scores/<context>/<int:revid>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revisions_v3(context, revid):
        """
        Compute the score of a score.

        Args:
            context: (todo): write your description
            revid: (str): write your description
        """
        try:
            score_request = build_score_request(
                scoring_system, request, context, rev_id=revid)
        except Exception as e:
            return responses.bad_request(str(e))

        return util.process_score_request(score_request, scoring_system)

    # /v3/scores/enwiki/reverted/4567890
    @bp.route("/v3/scores/<context>/<int:rev_id>/<model>/", methods=["GET", "POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def score_revision_v3(context, model, rev_id):
        """
        Displays the current revision score.

        Args:
            context: (todo): write your description
            model: (todo): write your description
            rev_id: (int): write your description
        """
        try:
            score_request = build_score_request(
                scoring_system, request, context, rev_id=rev_id,
                model_name=model)
        except Exception as e:
            return responses.bad_request(str(e))

        return util.process_score_request(score_request, scoring_system)

    return bp
