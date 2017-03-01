import traceback

from flask import request
from flask.ext.jsonpify import jsonify

from ... import preprocessors, responses
from .... import errors
from ...util import ParamError, read_bar_split_param


def configure(config, bp, scoring_system):

    @bp.route("/v2/precache/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def precache_v2():
        if 'wiki' not in request.args or 'revids' not in request.args:
            return responses.bad_request("'wiki' and 'revids' arguments are required")
        context = request.args.get('wiki')
        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        # Read the rev_ids
        try:
            rev_ids = set(read_bar_split_param(request, "revids", type=int))
        except ParamError as e:
            return responses.bad_request(str(e))
        if not rev_ids:
            return responses.bad_request(str(e))

        response_doc = {context: {}}
        precache_config = config['scoring_contexts'].get(context, {}).get('precache', {})
        if 'bot' in request.args and precache_config:
            models = []
            for model in precache_config:
                if 'nonbot_edit' not in precache_config[model]['on']:
                    models.append(model)
        else:
            models = precache_config.keys()

        for model_name in models:
            response_doc[context][model_name] = \
                {'version': scoring_system[context].model_version(model_name)}

        try:
            scores_doc = scoring_system.score(
                context, models, rev_ids, precache=True,
                include_model_info=None)
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

        return jsonify({'scores': response_doc})

    return bp
