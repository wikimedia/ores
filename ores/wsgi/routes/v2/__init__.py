from flask import render_template

from . import scores


def configure(config, bp, score_processor):

    @bp.route("/v2/", methods=["GET"])
    def v2_index():
        return render_template("v2.html")

    bp = scores.configure(config, bp, score_processor)

    return bp
