from flask.ext.jsonpify import jsonify


def no_content():
    return "", 204

def error(status, code, message):
    return jsonify({'error': {'code': code, 'message': message}}), status


def not_implemented(message=None):
    return error(501, 'not implemented',
                 message or "Route not implemented yet.")


def bad_request(message):
    return error(400, 'bad request', message)


def forbidden(message=None):
    return error(403, 'forbidden',
                 message or "This request requires authentication.")


def not_found(message=None):
    return error(404, 'not found',
                 message or "Nothing found at this location.")


def server_overloaded(message=None):
    return error(503, 'server overloaded',
                 message or ("Cannot process your request because the " +
                             "server is overloaded.  Try again in a" +
                             "few minutes."))


def unknown_error(message):
    return error(500, 'internal server error', message)
