import os

from flask import render_template, request, send_file

from . import ui, v1, v2, v3, versions

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

    @bp.app_errorhandler(404)
    def page_not_found(e):
        return render_template(
            '404.html',
            title=request.path,
            host=config['ores']['wsgi']['error_host'],
            alt=config['ores']['wsgi']['error_alt']), 404

    bp = ui.configure(config, bp)
    bp = versions.configure(config, bp)
    bp = v1.configure(config, bp, score_processor)
    bp = v2.configure(config, bp, score_processor)
    bp = v3.configure(config, bp, score_processor)

    return bp
