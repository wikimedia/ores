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
    if len(response.scores) > 0:
        context_doc['scores'] = {
            rev_id: {mn: format_v3_model_score(ms)
                     for mn, ms in model_scores.items()}
            for rev_id, model_scores in response.scores.items()}

    context_doc['models'] = response.model_info

    return jsonify({response.context.name: context_doc})


def format_v3_model_score(model_score):
    if isinstance(model_score, Exception):
        return util.format_error(model_score)
    else:
        return model_score


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
        return jsonify({'scores': context_models_doc})
    except Exception:
        return responses.unknown_error(traceback.format_exc())
