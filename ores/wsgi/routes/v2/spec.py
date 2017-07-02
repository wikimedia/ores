import json
from urllib.parse import urlparse

from flask import jsonify, render_template, request

from ... import preprocessors


def configure(config, bp, score_processor):

    # /spec/
    @bp.route("/v2/spec/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def v2_spec():
        return generate_spec(config)

    return bp


def generate_spec(config):
    return jsonify(json.loads(render_template(
        "v2_swagger.json",
        host=urlparse(request.url_root).netloc,
        scheme=config['ores']['wsgi']['scheme'])))
