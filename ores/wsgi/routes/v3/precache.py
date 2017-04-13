import logging

from flask import request

from . import scores
from ... import preprocessors, responses, util

logger = logging.getLogger(__name__)


def configure(config, bp, scoring_system):

    precache_map = util.build_precache_map(config)

    @bp.route("/v3/precache/", methods=["POST"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def precache_v3():
        event = request.get_json()
        if event is None:
            return responses.bad_request(
                "Must provide a POST'ed json as an event")

        try:
            score_request = util.build_score_request_from_event(
                precache_map, event)
        except KeyError as e:
            return responses.bad_request(
                "Must provide the '{key}' parameter".format(key=e.args[0]))
        if not score_request:
            return responses.no_content()
        else:
            return scores.process_score_request(score_request)

    return bp
