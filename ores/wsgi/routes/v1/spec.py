import os

import yaml
from flask.ext.jsonpify import jsonify


def configure(config, bp, score_processor):

    # /spec/
    @bp.route("/v1/spec/", methods=["GET"])
    def v1_spec():
        return generate_spec()

    return bp


def generate_spec():
    dir_name = os.path.dirname(os.path.abspath(__file__))
    swagger_doc = yaml.load(open(os.path.join(dir_name, "swagger.yaml")))
    return jsonify(swagger_doc)
