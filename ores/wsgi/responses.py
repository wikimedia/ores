import logging

from flask_jsonpify import jsonify

SERVER_OVERLOADED = 503
NOT_FOUND = 404
TIMEOUT = 504
TOO_MANY_REQUESTS = 429
logger = logging.getLogger(__name__)


def no_content():
    return "", 204


def error(status, code, message):
    return jsonify({'error': {'code': code, 'message': message}}), status


def not_implemented(message=None):
    return error(501, 'not implemented',
                 message or "Route not implemented yet.")


def model_info_lookup_error(exc):
    return bad_request("Model information could not be retrieved for {0}"
                       .format(exc))


def bad_request(message):
    return error(400, 'bad request', message)


def forbidden(message=None):
    return error(403, 'forbidden',
                 message or "This request requires authentication.")


def not_found(message=None):
    return error(NOT_FOUND, 'not found',
                 message or "Nothing found at this location.")


def server_overloaded(message=None):
    return error(SERVER_OVERLOADED, 'server overloaded',
                 message or ("Cannot process your request because the " +
                             "server is overloaded.  Try again in a" +
                             "few minutes."))


def unknown_error(message):
    logger.error(message)
    return error(500, 'internal server error', message)


def timeout_error(message=None):
    return error(TIMEOUT, 'request_timeout',
                 message or ("Cannot process your request because the " +
                             "server timed out."))


def too_many_requests_error(message=None):
    return error(TOO_MANY_REQUESTS, 'too_many_requests',
                 message or ("A limited number of parallel connections per " +
                             "IP is allowed."))
