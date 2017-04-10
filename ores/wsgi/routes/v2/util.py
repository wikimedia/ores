import traceback
from collections import defaultdict

from flask.ext.jsonpify import jsonify

from ... import responses, util


def format_v2_score_response(request, response):
    """
    {
        "scores": {
            "<context>": {
                "<model_name>": {
                    "scores": {
                        "<rev_id>": <score>,
                        "<rev_id>": <score>
                    },
                    "features": {
                        "<rev_id>": <features>,
                        "<rev_id>": <features>
                    },
                    "info": <model_info>,
                    "version": "<model_version>"
                }
                "<model_name>": {
                    "scores": {
                        "<rev_id>": <score>,
                        "<rev_id>": <score>
                    },
                    "features": {
                        "<rev_id>": <features>,
                        "<rev_id>": <features>
                    },
                    "info": <model_info>,
                    "version": "<model_version>"
                }
            }
        }
    }
    """
    return jsonify({"scores": {
        response.context.name: {
            model_name: format_v2_model(request, response, model_name)
            for model_name in response.request.model_names}}})


def format_v2_model(request, response, model_name):

    model_doc = defaultdict(dict)
    model_doc['version'] = response.context[model_name].version

    if request.model_info and model_name in response.model_info:
        model_doc['info'] = response.model_info[model_name]

    for rev_id, rev_scores in response.scores.items():
        if model_name in rev_scores:
            model_doc['scores'][rev_id] = rev_scores[model_name]

    for rev_id, rev_errors in response.errors.items():
        if model_name in rev_errors:
            model_doc['scores'][rev_id] = \
                util.format_error(rev_errors[model_name])

    for rev_id, rev_features in response.features.items():
        if model_name in rev_features:
                model_doc['features'][rev_id] = rev_features[model_name]

    return model_doc


def build_v2_context_model_map(score_request, scoring_system):
    """
    {
        "scores": {
            "<context>": {
                "<model_name>": {
                    "version": "<model_version>",
                    "info": <model_info>
                }
            },
            "<context>": {
                "<model_name>": {
                    "version": "<model_version>",
                    "info": <model_info>
                }
            }
        }
    """
    try:
        context_models_doc = {}
        for context_name, context in scoring_system.items():
            context_models_doc[context_name] = {}
            for model_name in context:
                model_doc = {'version': context.model_version(model_name)}
                if score_request.model_info:
                    model_doc['info'] = context.format_model_info(
                        model_name, score_request.model_info)
                context_models_doc[context_name][model_name] = model_doc
        return jsonify({'scores': context_models_doc})
    except Exception:
        return responses.unknown_error(traceback.format_exc())
