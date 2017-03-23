import json
from urllib.parse import urlparse

from flask import render_template, request
from flask.ext.jsonpify import jsonify

from ... import preprocessors


def configure(config, bp, score_processor):

    # /spec/
    @bp.route("/v3/spec/", methods=["GET"])
    @preprocessors.nocache
    @preprocessors.minifiable
    def v3_spec():
        return generate_spec()

    return bp


def generate_spec():
    return jsonify(json.loads(render_template(
        "v3_swagger.json",
        host=urlparse(request.url_root).netloc,
        scheme=urlparse(request.url_root).scheme)))
