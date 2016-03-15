from flask import render_template

from . import ui
from . import v1
from . import v2


def configure(config, bp, score_processor):

    @bp.route("/", methods=["GET"])
    def index():
        return render_template("home.html")

    bp = ui.configure(config, bp)
    bp = v1.configure(config, bp, score_processor)
    bp = v2.configure(config, bp, score_processor)

    return bp
