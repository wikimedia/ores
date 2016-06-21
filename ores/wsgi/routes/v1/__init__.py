from flask import request
from flask_swaggerui import render_swaggerui

from . import scores
from . import spec


def configure(config, bp, score_processor):

    bp = scores.configure(config, bp, score_processor)
    bp = spec.configure(config, bp, score_processor)

    @bp.route("/v1/", methods=["GET"])
    def v1_index():
        if "spec" in request.args:
            return spec.generate_spec()
        else:
            return render_swaggerui(swagger_spec_path="/v1/spec/")

    return bp
