import os

from flask import render_template, send_file

from . import versions
from . import ui
from . import v1
from . import v2
from . import v3

PWD = os.path.dirname(os.path.abspath(__file__))
GEAR_FAVICON = os.path.join(PWD, "../static/favicon/gear/favicon.ico")


def configure(config, bp, score_processor):

    @bp.route("/", methods=["GET"])
    def index():
        return render_template(
            "home.html", **config['ores'].get('home', {}))

    @bp.route("/favicon.ico", methods=["GET"])
    def favicon():
        # Tries to read from config or just loads the gear..
        return send_file(config['ores'].get('favicon', GEAR_FAVICON))

    bp = ui.configure(config, bp)
    bp = versions.configure(config, bp)
    bp = v1.configure(config, bp, score_processor)
    bp = v2.configure(config, bp, score_processor)
    bp = v3.configure(config, bp, score_processor)

    return bp
