import traceback

from flask.ext.jsonpify import jsonify

from ... import responses, util


def format_v3_score_response(response):
    """
    {
        "<context_name>": {
            "scores": {
                "<rev_id>": {
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    },
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    }
                },
                "<rev_id>": {
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    },
                    "<model_name>": {
                        "score": <score>,
                        "features": <features>
                    }
                }
            },
            "models": {
                "<model_name>": <model_info>,
                "<model_name>": <model_info>
            }
        }
    }
    """
    context_doc = {}
    if len(response.scores) > 0 or len(response.errors) > 0:
        context_doc['scores'] = {
            rev_id: {model_name: {'score': score}
                     for model_name, score in rev_scores.items()}
            for rev_id, rev_scores in response.scores.items()}

        for rev_id, rev_errors in response.errors.items():
            for model_name, error in rev_errors.items():
                context_doc['scores'][rev_id][model_name] = \
                    util.format_error(error)

        for rev_id, rev_features in response.features.items():
            for model_name, features in rev_features.items():
                context_doc['scores'][rev_id][model_name]['features'] = \
                    features

    if len(response.model_info) > 0:
        context_doc['models'] = {
            model_name: info_doc
            for model_name, info_doc in response.model_info.items()}

    return jsonify({response.context.name: context_doc})


def build_v3_context_model_map(score_request, scoring_system):
    """
    {
        "<context>": {
            "models": {
                "<model_name>": <model_info>,
                "<model_name>": <model_info>
            }
        },
        "<context>": {
            "models": {
                "<model_name>": <model_info>,
                "<model_name>": <model_info>
            }
        }
    }
    """
    try:
        context_models_doc = {}
        for context_name, context in scoring_system.items():
            context_models_doc[context_name] = {'models': {}}
            for model_name in context:
                model_doc = context.format_model_info(
                    model_name, score_request.model_info or ['version'])
                context_models_doc[context_name]['models'][model_name] = model_doc
        return jsonify(context_models_doc)
    except Exception:
        return responses.unknown_error(traceback.format_exc())
