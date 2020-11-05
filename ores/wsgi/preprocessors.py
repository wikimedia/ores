from functools import wraps

from flask import current_app, make_response, request


def minifiable(route):
    """
    Decorator for a flask route.

    Args:
        route: (array): write your description
    """
    @wraps(route)
    def minifiable_route(*args, **kwargs):
        """
        Minifiable route route a route.

        Args:
        """
        # Change the config
        current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = \
            False if request.args.get('format') == 'json' else True

        # Generate a response
        response = route(*args, **kwargs)

        # Explicitly return to default now that the result is generated
        current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

        return response

    return minifiable_route


def nocache(route):
    """
    Decorator to add a nocache route.

    Args:
        route: (str): write your description
    """
    @wraps(route)
    def nocache_route(*args, **kwargs):
        """
        Decorator to add a response to the route.

        Args:
        """
        response = make_response(route(*args, **kwargs))
        response.headers['Cache-Control'] = \
            "no-store, no-cache, max-age=0"
        response.headers['Pragma'] = 'no-cache'
        # Unix epoch
        response.headers['Expires'] = 'Thu, 01 Jan 1970 00:00:00 GMT'
        return response

    return nocache_route
