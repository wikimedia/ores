from flask import request
from flask.ext.jsonpify import jsonify

from ... import responses
from .... import errors
from ...util import (CacheParsingError, ParamError, parse_injection,
                     read_bar_split_param)


def configure(config, bp, score_processor):

    # /v2/scores/
    @bp.route("/v2/scores/", methods=["GET"])
    def scores_v2():
        scores_doc = {}

        # model_info param
        if 'model_info' in request.args:
            try:
                model_info_fields = set(read_bar_split_param(request, "model_info", type=str))
            except ParamError as e:
                return responses.bad_request(str(e))
        else:
            model_info_fields = None

        for context, scoring_context in score_processor.items():
            context_doc = {}
            for model, scorer_model in scoring_context.items():
                model_doc = {'version': scorer_model.version}

                if model_info_fields is not None:
                    info_doc = scorer_model.format_info(format='json')
                    if len(model_info_fields) > 0 and \
                       model_info_fields != {''}:
                        info_doc = {k: info_doc[k]
                                    for k in model_info_fields
                                    if k in info_doc}

                    model_doc['info'] = info_doc

                context_doc[model] = model_doc

            scores_doc[context] = context_doc

        return jsonify({'scores': scores_doc})

    # /v2/scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/v2/scores/<context>/", methods=["GET"])
    def score_model_revisions_v2(context):
        scores_doc = {context: {}}
        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        # models param
        if "models" in request.args:
            # Read the models param
            try:
                models = set(read_bar_split_param(request, "models", type=str))
            except ParamError as e:
                return responses.bad_request(str(e))

            # Check if all the models are available
            missing_models = models - score_processor[context].keys()
            if len(missing_models) > 0:
                return responses.bad_request("Models '{0}' not available for {1}."
                                             .format(list(missing_models), context))
        else:
            # Empty?  All the models!
            models = score_processor[context].keys()

        for model in models:
            scores_doc[context][model] = \
                {'version': score_processor[context][model].version}

        # model_info param
        if 'model_info' in request.args:
            try:
                model_info_fields = set(read_bar_split_param(request, "model_info", type=str))
            except ParamError as e:
                return responses.bad_request(str(e))

            for model in models:
                model_info_doc = \
                    score_processor[context][model].format_info(format='json')
                if len(model_info_fields) > 0 and model_info_fields != {''}:
                    model_info_doc = {k: model_info_doc[k]
                                      for k in model_info_fields
                                      if k in model_info_doc}

                scores_doc[context][model]['info'] = model_info_doc

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        if len(rev_ids) > 0:
            precache = "precache" in request.args

            try:
                for model in models:
                    model_scores, _ = score_processor.score(
                        context, model, rev_ids, precache=precache)
                    scores_doc[context][model]['scores'] = model_scores
            except errors.ScoreProcessorOverloaded:
                return responses.server_overloaded()

        return jsonify({'scores': scores_doc})

    # /v2/scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/v2/scores/<context>/<model>/", methods=["GET"])
    def score_revisions_v2(context, model):
        scores_doc = {context: {model: {}}}
        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in score_processor[context]:
            return responses.bad_request("Model '{0}' not available for {1}."
                                         .format(model, context))

        scores_doc[context][model] = \
            {'version': score_processor[context][model].version}

        if 'model_info' in request.args:
            try:
                model_info_fields = set(
                    read_bar_split_param(request, "model_info", type=str))
            except ParamError as e:
                return responses.bad_request(str(e))

            model_info_doc = \
                score_processor[context][model].format_info(format='json')
            if len(model_info_fields) > 0 and model_info_fields != {''}:
                model_info_doc = {k: model_info_doc[k]
                                  for k in model_info_fields
                                  if k in model_info_doc}

            scores_doc[context][model]['info'] = model_info_doc

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        if len(rev_ids) > 0:
            precache = "precache" in request.args

            try:
                model_scores, _ = score_processor.score(
                    context, model, rev_ids, precache=precache)
                scores_doc[context][model]['scores'] = model_scores
            except errors.ScoreProcessorOverloaded:
                return responses.server_overloaded()

        return jsonify({'scores': scores_doc})

    # /v2/scores/enwiki/reverted/4567890
    @bp.route("/v2/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    def score_revision_v2(context, model, rev_id):
        scores_doc = {context: {model: {}}}
        # Check to see if we have the context available in our score_processor
        if context not in score_processor:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in score_processor[context]:
            return responses.bad_request("Model '{0}' not available for {1}."
                                         .format(model, context))

        scores_doc[context][model] = \
            {'version': score_processor[context][model].version}

        if 'model_info' in request.args:
            try:
                model_info_fields = set(
                    read_bar_split_param(request, "model_info", type=str))
            except ParamError as e:
                return responses.bad_request(str(e))

            model_info_doc = \
                score_processor[context][model].format_info(format='json')
            if len(model_info_fields) > 0 and model_info_fields != {''}:
                model_info_doc = {k: model_info_doc[k]
                                  for k in model_info_fields
                                  if k in model_info_doc}

            scores_doc[context][model]['info'] = model_info_doc

        try:
            caches = parse_injection(request, rev_id)
        except CacheParsingError as e:
            return responses.bad_request("Unabled to parse params: {0}"
                                         .format(e))

        include_features = "features" in request.args
        precache = "precache" in request.args

        try:
            model_scores, feature_values = score_processor.score(
                context, model, [rev_id], caches=caches,
                precache=precache, include_features=include_features)
            scores_doc[context][model]['scores'] = model_scores
            if include_features:
                scores_doc[context][model]['features'] = feature_values
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()

        return jsonify({'scores': scores_doc})

    return bp
