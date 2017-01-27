import traceback

from flask import request
from flask.ext.jsonpify import jsonify

from ... import preprocessors, responses
from .... import errors
from ...util import (CacheParsingError, ParamError, nocache, parse_injection,
                     read_bar_split_param)


def configure(config, bp, scoring_system):

    # /v2/scores/
    @bp.route("/v2/scores/", methods=["GET"])
    @nocache
    @preprocessors.minifiable
    def scores_v2():
        # model_info param
        if 'model_info' in request.args:
            try:
                include_model_info = \
                    set(read_bar_split_param(request, "model_info", type=str))
                if include_model_info == {''}:
                    include_model_info = "all"
            except ParamError as e:
                return responses.bad_request(str(e))
        else:
            include_model_info = None

        response_doc = {}
        for context_name, scoring_context in scoring_system.items():

            response_doc[context_name] = scoring_system.format_model_info(
                context_name, include_model_info=include_model_info)

        return jsonify({'scores': response_doc})

    # /v2/scores/enwiki/?models=reverted&revids=456789|4567890
    @bp.route("/v2/scores/<context>/", methods=["GET"])
    @nocache
    @preprocessors.minifiable
    def score_model_revisions_v2(context):
        response_doc = {context: {}}
        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
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
            missing_models = models - scoring_system[context].keys()
            if len(missing_models) > 0:
                return responses.bad_request("Models '{0}' not available for {1}."
                                             .format(list(missing_models), context))
        else:
            # Empty?  All the models!
            models = scoring_system[context].keys()

        # model_info param
        if 'model_info' in request.args:
            try:
                include_model_info = \
                    set(read_bar_split_param(request, "model_info", type=str))
                if include_model_info == {''}:
                    include_model_info = "all"
            except ParamError as e:
                return responses.bad_request(str(e))
        else:
            include_model_info = None

        for model_name in models:
            response_doc[context][model_name] = \
                {'version': scoring_system[context].model_version(model_name)}

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        if len(rev_ids) > 0:
            precache = "precache" in request.args

            try:
                scores_doc = scoring_system.score(
                    context, models, rev_ids, precache=precache,
                    include_model_info=include_model_info)
            except errors.ScoreProcessorOverloaded:
                return responses.server_overloaded()
            except Exception:
                return responses.unknown_error(traceback.format_exc())

            for model_name in models:
                response_doc[context][model_name]['scores'] = {}
                for rev_id in rev_ids:
                    if 'error' in scores_doc['scores'][rev_id]:
                        response_doc[context][model_name]['scores'][rev_id] = \
                            scores_doc['scores'][rev_id]
                    else:
                        response_doc[context][model_name]['scores'][rev_id] = \
                            scores_doc['scores'][rev_id][model_name]['score']

                if include_model_info:
                    response_doc[context][model_name]['info'] = \
                        scores_doc['models'][model_name]
        elif include_model_info is not None:
            models_info_doc = scoring_system.format_model_info(
                context, models, include_model_info=include_model_info)
            for model_name, model_info_doc in models_info_doc.items():
                response_doc[context][model_name]['info'] = model_info_doc

        return jsonify({'scores': response_doc})

    # /v2/scores/enwiki/reverted/?revids=456789|4567890
    @bp.route("/v2/scores/<context>/<model>/", methods=["GET"])
    @nocache
    @preprocessors.minifiable
    def score_revisions_v2(context, model):
        response_doc = {context: {model: {}}}
        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in scoring_system[context]:
            return responses.bad_request("Model '{0}' not available for {1}."
                                         .format(model, context))

        response_doc[context][model] = \
            {'version': scoring_system[context].model_version(model)}

        if 'model_info' in request.args:
            try:
                include_model_info = set(
                    read_bar_split_param(request, "model_info", type=str))
                if include_model_info == {''}:
                    include_model_info = "all"
            except ParamError as e:
                return responses.bad_request(str(e))
        else:
            include_model_info = None

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))

        if len(rev_ids) > 0:
            precache = "precache" in request.args

            try:
                scores_doc = scoring_system.score(
                    context, [model], rev_ids, precache=precache,
                    include_model_info=include_model_info)
            except errors.ScoreProcessorOverloaded:
                return responses.server_overloaded()
            except Exception:
                return responses.unknown_error(traceback.format_exc())

            response_doc[context][model]['scores'] = {}
            for rev_id in rev_ids:
                if 'error' in scores_doc['scores'][rev_id]:
                    response_doc[context][model]['scores'][rev_id] = \
                        scores_doc['scores'][rev_id]
                else:
                    response_doc[context][model]['scores'][rev_id] = \
                        scores_doc['scores'][rev_id][model]['score']

            if include_model_info:
                response_doc[context][model]['info'] = \
                    scores_doc['models'][model]
        elif include_model_info is not None:
            models_info_doc = scoring_system.format_model_info(
                context, [model], include_model_info=include_model_info)
            for model_name, model_info_doc in models_info_doc.items():
                response_doc[context][model_name]['info'] = model_info_doc

        return jsonify({'scores': response_doc})

    # /v2/scores/enwiki/reverted/4567890
    @bp.route("/v2/scores/<context>/<model>/<int:rev_id>/", methods=["GET", "POST"])
    @nocache
    @preprocessors.minifiable
    def score_revision_v2(context, model, rev_id):
        response_doc = {context: {model: {}}}
        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No models available for {0}"
                                       .format(context))

        if model not in scoring_system[context]:
            return responses.bad_request("Model '{0}' not available for {1}."
                                         .format(model, context))

        response_doc[context][model] = \
            {'version': scoring_system[context].model_version(model)}

        if 'model_info' in request.args:
                try:
                    include_model_info = set(
                        read_bar_split_param(request, "model_info", type=str))
                    if include_model_info == {''}:
                        include_model_info = "all"
                except ParamError as e:
                    return responses.bad_request(str(e))
        else:
            include_model_info = None

        try:
            caches = parse_injection(request, rev_id)
        except CacheParsingError as e:
            return responses.bad_request("Unabled to parse params: {0}"
                                         .format(e))

        include_features = "features" in request.args
        precache = "precache" in request.args

        try:
            scores_doc = scoring_system.score(
                context, [model], [rev_id], injection_caches=caches,
                precache=precache, include_features=include_features,
                include_model_info=include_model_info)
            if 'error' in scores_doc['scores'][rev_id]:
                response_doc[context][model]['scores'] = \
                    {rev_id: scores_doc['scores'][rev_id]}
            else:
                response_doc[context][model]['scores'] = \
                    {rev_id: scores_doc['scores'][rev_id][model]['score']}
                if include_features:
                    response_doc[context][model]['features'] = \
                        {rev_id: scores_doc['scores'][rev_id][model]['features']}
            if include_model_info:
                response_doc[context][model]['info'] = \
                    scores_doc['models'][model]
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

        return jsonify({'scores': response_doc})

    return bp
