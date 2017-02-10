import json

from flask import request
from flask.ext.jsonpify import jsonify as jsonify_


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
        raise ParamError("Could not interpret {0}. {1}".format(param, str(e)))


def read_bar_split_param(request, param, default=None, type=str):
    values = read_param(request, param, default=default)
    if values is None:
        return []

    try:
        return [type(value) for value in values.split("|")]
    except (ValueError, TypeError) as e:
        raise ParamError("Could not interpret {0}. {1}"
                         .format(param, str(e)))


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


def jsonify(doc):
    minify = request.args.get('format') == 'json'
    separators = None if minify else "  "
    return jsonify_(doc, separators=separators)
