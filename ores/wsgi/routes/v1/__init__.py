from flask import render_template

from . import scores


def configure(config, bp, score_processor):

    @bp.route("/v1/", methods=["GET"])
    def v1_index():
        return render_template("v1.html")

    bp = scores.configure(config, bp, score_processor)

    return bp
