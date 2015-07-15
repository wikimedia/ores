
from . import scores


def configure(config, bp, score_processor):

    @bp.route("/", methods=["GET"])
    def index():
        return "Hi!  I'm ORES.  :D"

    bp = scores.configure(config, bp, score_processor)

    return bp
