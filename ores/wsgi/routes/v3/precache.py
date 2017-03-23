import json
import logging
from urllib.parse import unquote

from flask import request

from . import scores
from ... import preprocessors, responses, util

logger = logging.getLogger(__name__)


def configure(config, bp, scoring_system):

    precache_map = util.build_precache_map(config)

    @bp.route("/v3/precache/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def precache_v3():
        if 'event' not in request.args:
            return responses.bad_request(
                "Must provide an 'event' parameter")
        try:
            event = json.loads(unquote(request.args['event']).strip())
        except json.JSONDecodeError:
            return responses.bad_request(
                "Can not parse event argument as JSON blob")

        score_request = util.build_score_request_from_event(precache_map, event)

        if not score_request:
            return responses.no_content()
        else:
            return scores.process_score_request(score_request)

    return bp
