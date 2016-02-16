
from . import scores
from . import ui
from . import v2


def configure(config, bp, score_processor):

    @bp.route("/", methods=["GET"])
    def index():
        return "Hi!  I'm ORES.  :D"

    bp = scores.configure(config, bp, score_processor)
    bp = ui.configure(config, bp)
    bp = v2.configure(config, bp, score_processor)

    return bp
