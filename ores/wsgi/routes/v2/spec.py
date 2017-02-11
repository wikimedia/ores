import json
from urllib.parse import urlparse

from flask import render_template, request
from flask.ext.jsonpify import jsonify

from ... import preprocessors


def configure(config, bp, score_processor):

    # /spec/
    @bp.route("/v2/spec/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def v2_spec():
        return generate_spec()

    return bp


def generate_spec():
    return jsonify(json.loads(render_template(
        "v2_swagger.json",
        host=urlparse(request.url_root).netloc,
        scheme=urlparse(request.url_root).scheme)))
