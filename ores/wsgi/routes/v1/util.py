from collections import defaultdict

from flask.ext.jsonpify import jsonify

from ... import util


def format_v1_score_response(response, limit_to_model=None):
    """
    The response format looks like this::

        {
            "<rev_id>": {
                "<model_name>": <score>
                "<model_name>": <score>
            },
            "<rev_id>": {
                "<model_name>": <score>
                "<model_name>": <score>
            }
        }
    """
    response_doc = defaultdict(dict)
    for rev_id, rev_scores in response.scores.items():
        for model_name, score in rev_scores.items():
            response_doc[rev_id][model_name] = score

    for rev_id, rev_errors in response.errors.items():
        for model_name, error in rev_errors:
            response_doc[rev_id][model_name] = util.format_error(error)

    if limit_to_model is not None:
        return jsonify({rev_id: model_scores[limit_to_model]
                        for rev_id, model_scores in response_doc.items()})
    else:
        return jsonify(response_doc)


def format_some_model_info(scoring_system, request, limit_to_model=None):
    scoring_system.check_context_models(request)
    model_infos = {}
    for model_name in request.model_names:
        model_info = \
            scoring_system[request.context_name].format_model_info(
                model_name, fields=[''])
        model_infos[model_name] = model_info

    if limit_to_model is None:
        return jsonify({'models': model_infos})
    else:
        return jsonify(model_infos[model_name])
