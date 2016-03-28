import json
from collections import defaultdict

from flask.ext.jsonpify import jsonify


class CacheParsingError(Exception):
    pass


class ParamError(Exception):
    pass


def read_param(request, param, default=None, type=str):
    try:
        value = request.args.get(param, request.form.get(param))
        if value is None:
            return default
        else:
            return type(value)
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}"
                         .format(param, str(e)))


def read_bar_split_param(request, param, default=None, type=str):
    values = read_param(request, param, default=default)
    if values is None:
        return []

    try:
        return [type(value) for value in values.split("|")]
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}"
                         .format(param, str(e)))


def format_output(context, scores, model_info, warning=None, notice=None):
    """
    Formats a JSON blob of scores for API v2

    :Parameters:
        context: `str`
            Name of wiki
        scores : `dict`
            A JSONable dictionary of scores by revision ID and model.
        model_info : `dict`
            Information about mdoels
        warning: `dict`
            A warning if any
        notice: `dict`
            notice of deployment, etc. if any
    """
    output = defaultdict(dict)
    if notice:
        output['notice'] = notice
    if warning:
        output['warning'] = warning
    output['scores'] = {context: {}}
    for model in model_info:
        output['scores'][context][model] = model_info[model]
    output['scores'][context][model]['scores'] = {}
    for model in scores:
        output['scores'][context][model]['scores'] = {}
        for rev_id in scores[model]:
            output['scores'][context][model]['scores'][rev_id] = scores[model][rev_id]
    return jsonify(output)


def parse_injection(request, rev_id):
    """Parse values for features / datasources of interest."""
    cache = {}
    try:
        if 'inject' in request.values:
            cache = json.loads(request.values['inject'])

        for k, v in request.values.items():
            if k.startswith(("feature.", "datasource.")):
                cache[k] = json.loads(v)

        return {rev_id: cache} if len(cache) > 0 else None
    except Exception as e:
        raise CacheParsingError(e)
