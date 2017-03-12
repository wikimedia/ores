import json
import traceback

from flask import request
from flask.ext.jsonpify import jsonify

from urllib.parse import unquote

from ... import preprocessors, responses
from .... import errors


def configure(config, bp, scoring_system):

    @bp.route("/v2/precache/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def precache_v2():
        try:
            data = json.loads(unquote(request.args.get('data', '{}')).strip())
        except json.JSONDecodeError:
            return responses.bad_request("Can not parse data argument")
        if 'database' not in data or 'rev_id' not in data:
            return responses.bad_request("'database' and 'rev_id' arguments are required")
        context = data['database']
        # Check to see if we have the context available in our score_processor
        if context not in scoring_system:
            return responses.not_found("No scorers available for {0}"
                                       .format(context))

        # Read the rev_ids
        rev_id = data['rev_id']

        response_doc = {context: {}}
        precache_config = config['scoring_contexts'].get(context, {}).get('precache', {})
        performer_user_groups = data.get('performer', {}).get('user_groups', [])
        if precache_config and performer_user_groups:
            models = []
            for model in precache_config:
                if ('nonbot_edit' not in precache_config[model]['on'] and
                        'bot' not in performer_user_groups):
                    models.append(model)
        else:
            models = precache_config.keys()

        for model_name in models:
            response_doc[context][model_name] = \
                {'version': scoring_system[context].model_version(model_name)}

        try:
            scores_doc = scoring_system.score(
                context, models, [rev_id], precache=True,
                include_model_info=None)
        except errors.ScoreProcessorOverloaded:
            return responses.server_overloaded()
        except Exception:
            return responses.unknown_error(traceback.format_exc())

        for model_name in models:
            response_doc[context][model_name]['scores'] = {}
            if 'error' in scores_doc['scores'][rev_id]:
                response_doc[context][model_name]['scores'][rev_id] = \
                    scores_doc['scores'][rev_id]
            else:
                response_doc[context][model_name]['scores'][rev_id] = \
                    scores_doc['scores'][rev_id][model_name]['score']

        return jsonify({'scores': response_doc})

    return bp
