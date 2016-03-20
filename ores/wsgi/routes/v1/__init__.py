from flask import render_template

from . import scores
from . import spec


def configure(config, bp, score_processor):

    @bp.route("/v1/", methods=["GET"])
    def v1_index():
        return render_template("swagger-ui.html", swagger_spec="/v1/spec")

    bp = scores.configure(config, bp, score_processor)
    bp = spec.configure(config, bp, score_processor)

    return bp
