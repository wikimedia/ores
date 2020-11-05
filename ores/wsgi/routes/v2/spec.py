import json
from urllib.parse import urlparse

from flask import jsonify, render_template, request

from ... import preprocessors


def configure(config, bp, score_processor):
    """
    Configure a route specification.

    Args:
        config: (dict): write your description
        bp: (todo): write your description
        score_processor: (bool): write your description
    """

    # /spec/
    @bp.route("/v2/spec/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def v2_spec():
        """
        Generate spec specification.

        Args:
        """
        return generate_spec(config)

    return bp


def generate_spec(config):
    """
    Generate a json specification.

    Args:
        config: (todo): write your description
    """
    return jsonify(json.loads(render_template(
        "v2_swagger.json",
        host=urlparse(request.url_root).netloc,
        scheme=config['ores']['wsgi']['scheme'])))
