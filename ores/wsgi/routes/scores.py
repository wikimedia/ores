from flask import request
from flask.ext.jsonpify import jsonify

from .. import responses
from ..util import ParamError, read_bar_split_param


def configure(config, bp, scorers):

    # /scores/
    @bp.route("/scores/", methods=["GET"])
    def scores():
        wikis = [wiki for wiki in scorers]

        wikis.sort()

        return jsonify({'wikis': wikis})

    # /scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/scores/<wiki>/", methods=["GET"])
    def score_model_revisions(wiki):

        # Check to see if we have the wiki
        if wiki in scorers:
            scorer = scorers[wiki]
        else:
            return responses.not_found("No scorers available for {0}" \
                                       .format(wiki))

        # If no model is specified, return information on available models
        if "models" not in request.args:
            # Return the models that we have
            return jsonify({"models": list(scorers[wiki].scorer_models.keys())})

        # Read the params
        try:
            models = set(read_bar_split_param(request, "models", type=str))
        except ParamError as e:
            return responses.bad_request(str(e))

        # Check if all the models are available
        missing_models = models - scorer.scorer_models.keys()
        if len(missing_models) > 0:
            return responses.bad_request("Models '{0}' not available for {1}." \
                                         .format(list(missing_models), wiki))


        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        # Generate scores for each model and merge them together
        scores = defaultdict(dict)
        for model in models:
            model_scores = scorer.score(rev_ids, model=model)
            for rev_id in model_scores:
                scores[rev_id].update(model_scores[rev_id])

        return jsonify(scores)


    # /scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/scores/<wiki>/<model>/", methods=["GET"])
    def score_revisions(wiki, model):

        # Check to see if we have the wiki available in our scorers
        if wiki in scorers:
            scorer = scorers[wiki]
        else:
            return responses.not_found("No models available for {0}" \
                                       .format(wiki))

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        if len(rev_ids) == 0:
            return responses.bad_request("No revids provided.")

        # If the model exists, score revisions with it and return the result
        if model not in scorer.scorer_models:
            return responses.bad_request("Model '{0}' not available for {1}." \
                                         .format(model, wiki))
        else:
            return jsonify(scorer.score(rev_ids, model=model))


    # /scores/enwiki/reverted/4567890
    @bp.route("/scores/<wiki>/<model>/<int:rev_id>/", methods=["GET"])
    def score_revision(wiki, model, rev_id):

        # Check to see if we have the wiki available in our scorers
        if wiki in scorers:
            scorer = scorers[wiki]
        else:
            return responses.not_found("No models available for {0}" \
                                       .format(wiki))

        # If the model exists, score revisions with it and return the result
        if model not in scorer.scorer_models:
            return responses.not_found("Model '{0}' not available for {1}." \
                                         .format(model, wiki))
        else:
            return jsonify(scorer.score([rev_id], model=model))

    return bp
