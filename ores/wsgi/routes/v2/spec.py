import os

import yaml
from flask.ext.jsonpify import jsonify

from ... import preprocessors


def configure(config, bp, score_processor):

    # /spec/
    @bp.route("/v2/spec/", methods=["GET"])
    @preprocessors.nocache
    def v2_spec():
        return generate_spec()

    return bp


def generate_spec():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    swagger_doc = yaml.safe_load(open(os.path.join(dir_name, "swagger.yaml")))
    return jsonify(swagger_doc)
