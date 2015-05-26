from flask import request
from flask.ext.jsonpify import jsonify

from .. import responses
from ..util import ParamError, read_bar_split_param


def configure(config, bp, scorer_map, cache):

    # /scores/
    @bp.route("/scores/", methods=["GET"])
    def scores():
        scorers = [wiki for wiki in scorer_map]

        scorers.sort()

        return jsonify({'scorers': scorers})

    # /scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/scores/<wiki>/", methods=["GET"])
    def scores_revisions(wiki):

        # Check to see if we have the wiki
        if wiki in scorer_map:
            scorer = scorer_map[wiki]
        else:
            return responses.not_found("No scorers available for {0}" \
                                       .format(wiki))

        # If no model is specified, return information on available models
        if "models" not in request.args:
            # Return the models that we have
            return jsonify({"models": list(scorer_map[wiki].model_map.keys())})

        # Read the params
        try:
            model_names = set(read_bar_split_param(request, "models", type=str))
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        # Check that all requested models are available
        missing_models = model_names - scorer.models.keys()
        if len(missing_models) > 0:
            message = ("Models {0} is not available for {1}.  " +
                       "Available models: {2}") \
                      .format(list(missing_models), wiki,
                              list(scorer.models.keys()))

            return responses.bad_request(message)

        # Lookup cached scores
        scores = cache.lookup_many(rev_ids, wiki, model_names)
        missing_rev_ids = rev_ids - scores.keys()

        # TODO: Pre-cache datasources for missing_rev_ids and distribute
        # processing to celery
        # For now, just process missing rev_ids in batch
        scores = {rev_id:score for rev_id, score in
                  zip(rev_ids, scorer.score_many(missing_rev_ids,
                                                 models=model_names))}

        return jsonify(scores)

    return bp
