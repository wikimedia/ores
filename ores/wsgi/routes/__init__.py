
from . import scores
from . import ui
from . import v2


def configure(config, bp, score_processor):

    @bp.route("/", methods=["GET"])
    def index():
        return ui.render_template("home.html")

    bp = scores.configure(config, bp, score_processor)
    bp = ui.configure(config, bp)
    bp = v2.configure(config, bp, score_processor)

    return bp
