from functools import wraps

from flask import current_app, request


def minifiable(f):
    @wraps(f)
    def wrapped_f(*args, **kwargs):
        current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = \
            request.args.get('format') != 'json'

        return f(*args, **kwargs)

    return wrapped_f
