import traceback
from collections import defaultdict

from flask import render_template, request
from flask.ext.jsonpify import jsonify

from . import responses
from .util import ParamError, read_bar_split_param


def configure(config, bp, scorer_map):

    # /
    @bp.route("/", methods=["GET"])
    def scores():
        scorers = [wiki for wiki in scorer_map]

        scorers.sort()

        return jsonify({'scorers': scorers})

    # /enwiki?models=reverted&revids=456789|4567890
    @bp.route("/<wiki>/", methods=["GET"])
    def score_revisions(wiki):

        try:
            scorer = scorer_map[wiki]
        except KeyError:
            return responses.not_found("No scorers available for {0}" \
                                       .format(wiki))


        if "models" not in request.args:
            # Return the models that we have
            return jsonify({"models": list(scorer_map[wiki].model_map.keys())})
        else:
            try:
                model_names = read_bar_split_param(request, "models", str)
                rev_ids = read_bar_split_param(request, "revids", int)
            except ParamError as e:
                return responses.bad_request(str(e))

        scores = {}
        for rev_id in rev_ids:

            try:
                score = scorer.score(rev_id, models=model_names)
            except Exception as e:
                score = {"error": {'type': str(type(e)), 'message': str(e),
                                   'traceback': traceback.format_exc()}}

            scores[rev_id] = score

        return jsonify(scores)

    return bp
