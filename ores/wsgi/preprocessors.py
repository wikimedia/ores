from functools import wraps

from flask import current_app, request


def minifiable(f):
    @wraps(f)
    def wrapped_f(*args, **kwargs):
        format_ = request.args.get('format')
        if format_ == 'json':
            current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        return f(*args, **kwargs)

    return wrapped_f
